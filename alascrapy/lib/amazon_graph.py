import logging

from py2neo import authenticate, Graph, Relationship

from alascrapy.lib.conf import get_project_conf


class CategoryTree(object):
    
    def __init__(self, country):
        project_conf = get_project_conf()
        neo_host = project_conf.get("NEO4J", "host")
        user = project_conf.get("NEO4J", "username")
        password = project_conf.get("NEO4J", "password")
        logging.getLogger("py2neo.batch").setLevel(logging.WARNING)
        logging.getLogger("py2neo.cypher").setLevel(logging.WARNING)
        logging.getLogger("httpstream").setLevel(logging.WARNING)
        authenticate(neo_host, user, password)
        self.graph = Graph("http://%s/db/data/" % neo_host)
        try:
            self.graph.schema.create_uniqueness_constraint("Category", "id")
        except:
            pass
        self.categories = self.get_categories(country)

    def merge_node(self, node, country, do_not_load=False):
        category_id = "%s%s" % (country, str(node['BrowseNodeId']))
        category = self.graph.merge_one('Category', 'id', category_id)
        if 'name' not in category.properties:
            category['name'] = node['Name']
            category['is_root'] = int(node.get('IsCategoryRoot', 0))
            category['do_not_load'] = bool(do_not_load)
            category['country'] = country
            category.push()

        if not category_id in self.categories:
            self.categories[category_id] = self.category_node_dict(category)

        return category

    def relationship(self, parent, child):
        return Relationship(parent, 'HAS_CHILD', child)

    def relationship_exists(self, parent, child):
        if len(list(self.graph.match(start_node=parent,
                                     end_node=child,
                                     rel_type='HAS_CHILD'))) > 0:
            return True
        return False

    def create_relationship(self, relationship):
        self.graph.create_unique(relationship)
        relationship.push()

    def create_relationships(self, parent, children):
        for child in children:
            self.create_relationship(parent, child)


    def add_new_category(self, browsenode, amazon_api, country):
        # browse_node expected format
        #{u'Ancestors': {u'BrowseNode': {u'Ancestors': {u'BrowseNode': {u'BrowseNodeId': u'560798',
        #                                                               u'Name': u'Electronics & Photo'}},
        #                                u'BrowseNodeId': u'560800',
        #                                u'IsCategoryRoot': u'1',
        #                                u'Name': u'Categories'}},
        # u'BrowseNodeId': u'1340509031',
        # u'Children': {u'BrowseNode': [{u'BrowseNodeId': u'560826',
        #                                u'Name': u'Accessories'},
        #                               {u'BrowseNodeId': u'2829144031',
        #                                u'Name': u'Big Button Mobile Phones'},
        #                              {u'BrowseNodeId': u'430574031',
        #                               u'Name': u'Mobile Broadband'},
        #                              {u'BrowseNodeId': u'5362060031',
        #                               u'Name': u'Mobile Phones & Smartphones'},
        #                              {u'BrowseNodeId': u'213005031',
        #                               u'Name': u'SIM Cards'},
        #                              {u'BrowseNodeId': u'3457450031',
        #                               u'Name': u'Smartwatches'}]},
        # u'Name': u'Mobile Phones & Communication'}
        added_categories = []
        do_not_load = True

        current_browsenode = browsenode
        # Determine the value of do not load according to the youngest ancestor's do_not_load
        while 'Ancestors' in current_browsenode:
            current_id = "%s%s" % (country, current_browsenode['BrowseNodeId'])
            current_node = self.categories.get(current_id, None)
            if not current_node:
                if type(current_browsenode['Ancestors']) is dict:
                    current_browsenode = current_browsenode['Ancestors']
                elif type(current_browsenode['Ancestors']) is list:
                    current_browsenode = current_browsenode['Ancestors'][0]
                    # This shouldn't happen. But if it does better to log and continue with the first one
            else:
                do_not_load = bool(current_node['do_not_load'])
                break

        # Create the missing nodes and relationships

        child = self.merge_node(browsenode, country, do_not_load)
        added_categories.append(child)

        current_browsenode = browsenode
        while 'Ancestors' in current_browsenode and int(current_browsenode.get("IsCategoryRoot", 0))!=1:
            if type(current_browsenode['Ancestors']) is dict:
                parent_browsenode_id = current_browsenode['Ancestors']['BrowseNode']['BrowseNodeId']
            elif type(current_browsenode['Ancestors']) is list:
                # This shouldn't happen. But if it does better to log and continue with the first one
                parent_browsenode_id = current_browsenode['Ancestors'][0]['BrowseNode']['BrowseNodeId']

            parent_graph_id="%s%s" % (country,parent_browsenode_id)
            parent_node = self.categories.get(parent_graph_id, None)
            if parent_node:
                parent = self.get_category(parent_graph_id)
                relationship = self.relationship(parent, child)
                self.create_relationship(relationship)
                break
            else:
                parent_browsenode = amazon_api.get_node(parent_browsenode_id)
                if type(parent_browsenode) is dict:
                    parent = self.merge_node(parent_browsenode, country,
                                             do_not_load)
                    relationship = self.relationship(parent, child)
                    self.create_relationship(relationship)
                    added_categories.append(parent)
                    current_browsenode = parent_browsenode
                elif parent_browsenode == "AWS.InvalidParameterValue":
                    print "Deleting node %s and all its children" % str(parent_browsenode_id)
                    self.delete_category(parent_browsenode_id)
                    break
                else:
                    #self.logger.warning("Unknown error from amazon API.")
                    print 'Unknown error from amazon API. %s' % parent_browsenode
                    break

        for category in added_categories:
            category_id = "%s%s" % (country, category['id'])
            length = self.get_shortest_length_to_root(category_id)
            category['shortest_length_root'] = length
            category.push()
            self.categories[category_id] = self.category_node_dict(category)

        new_category_id = "%s%s" % (country, browsenode['BrowseNodeId'])
        return self.categories.get(new_category_id)

    def category_node_dict(self, category_node):
        result = {
            'is_root': category_node['is_root'],
            'id': category_node['id'],
            'name': category_node['name'],
            'do_not_load': category_node['do_not_load'],
            'shortest_length_root': category_node['shortest_length_root']
        }
        return result


    def get_categories(self, country):
        categories = {}
        records = self.graph.find('Category', property_key='country',
                                   property_value=country)
        for category in records:
            categories[category['id']] = self.category_node_dict(category)
        return categories


    def get_category(self, category_id):
        category = self.graph.find_one('Category', property_key='id', property_value=category_id)

        if category:
            return self.category_node_dict(category)

    def is_orphan(self, category_id):
        category = self.get_category(category_id)
        if not category:
            return True

        if not bool(category['is_root']):
            query = """MATCH p=a-[:HAS_CHILD*]->n
                       WHERE n.id = {id} AND a.is_root=1
                       RETURN p
                       LIMIT 1"""
            cypher = self.graph.cypher
            path = cypher.execute_one(query, id=category_id)
            if not path:
                return True
        return False                 

    def get_children(self, category_id):
        query = """MATCH (n)-[r:HAS_CHILD*]->(m)
                   WHERE n.id = {id}
                   RETURN m"""
        cypher = self.graph.cypher
        children = cypher.execute(query, id=category_id)
        return children

    def delete_category(self, category_id):
        cypher = self.graph.cypher
        children = self.get_children(category_id)

        delete_query = """
            MATCH (n {id:'%s'})
            OPTIONAL MATCH n-[r]-()
            DELETE n,r
        """
        if children:
            for record in children:
                child = record[0]
                cypher.execute_one(delete_query % child["id"])
        cypher.execute_one(delete_query % category_id)

    def get_shortest_length_to_root(self, category_id):
        query = """MATCH p=a-[:HAS_CHILD*]->n
                   WHERE n.id={id} AND a.is_root=1
                   RETURN length(p)
                   ORDER BY length(p) DESC
                   LIMIT 1"""
        cypher = self.graph.cypher
        length = cypher.execute_one(query, id=category_id)
        return length