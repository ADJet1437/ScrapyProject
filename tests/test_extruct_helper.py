import unittest
import alascrapy.lib.extruct_helper as extruct_helper

from scrapy.http.response.text import TextResponse


class TestExtructHelper(unittest.TestCase):

    # TODO: update and add test cases
    def test_review_item_from_review_json_ld_full_review(self):
        html_text = '''<script type="application/ld+json">
                       {
                          "@context": "http://schema.org/",
                          "@type": "Review",
                          "itemReviewed": {
                            "@type": "Product",
                            "name": "OnePlus 5"
                          },
                          "author": {
                            "@type": "Person",
                            "name": "Joe"
                          },
                          "reviewRating": {
                            "@type": "Rating",
                            "ratingValue": "7",
                            "bestRating": "10"
                          },
                          "publisher": {
                            "@type": "Organization",
                            "name": "CNET"
                          },
                          "datePublished":"2017-08-07",
                          "headline":"OnePlus 5 review",
                          "description":"The OnePlus 5 is one of the best phones you can buy today"
                        }
                        </script>'''
        json_ld = extruct_helper.extract_json_ld(html_text, 'Review')
        review = extruct_helper.review_item_from_review_json_ld(json_ld)
        self.assertIsNotNone(review)
        self.assertEqual(review['ProductName'], 'OnePlus 5')
        self.assertEqual(review['Author'], 'Joe')
        self.assertEquals(review['TestDateText'], '2017-08-07')
        self.assertEqual(int(review['SourceTestRating']), 7)
        self.assertEqual(int(review['SourceTestScale']), 10)
        self.assertEqual(review['TestTitle'], 'OnePlus 5 review')
        self.assertEqual(review['TestSummary'], 'The OnePlus 5 is one of the best phones you can buy today')

    def test_review_item_from_review_json_ld_default_best_rating(self):
        html_text = '''<script type="application/ld+json">
                       {
                           "@context":"http://schema.org/",
                           "@type":"Review",
                           "itemReviewed":{"@type":"Product","name":"OnePlus 5"},
                           "reviewRating":{"@type":"Rating","ratingValue":5}
                       }
                       </script>'''
        json_ld = extruct_helper.extract_json_ld(html_text, 'Review')
        review = extruct_helper.review_item_from_review_json_ld(json_ld)
        self.assertIsNotNone(review)
        self.assertEqual(int(review['SourceTestScale']), 5)

    def test_review_item_from_review_json_ld_rating_less_than_the_default_worst(self):
        html_text = '''<script type="application/ld+json">
                               {
                                   "@context":"http://schema.org/",
                                   "@type":"Review",
                                   "itemReviewed":{"@type":"Product","name":"OnePlus 5"},
                                   "reviewRating":{"@type":"Rating","ratingValue":0}
                               }
                               </script>'''
        json_ld = extruct_helper.extract_json_ld(html_text, 'Review')
        review = extruct_helper.review_item_from_review_json_ld(json_ld)
        self.assertIsNotNone(review)
        self.assertEqual(review['SourceTestRating'], '')

    # Now we only extract info from RDFa when scraping alphr.com, add more test cases
    # using RDFa markups with different syntax later if necessary
    def test_get_review_items_from_rdfa_using_alphr_syntax(self):
        # This is extract from http://alphr.com/go/1006047 on 2017/08/08
        html_text = '''
                        <body id="pid-htc-1006047-htc-u11-review-htcs-flagship-is-a-squeezy-pleaser" class="html not-front not-logged-in page-node page-node- page-node-1006047 node-type-review one-sidebar sidebar-second narrow-stacked snap" 
                         prefix="v: http://rdf.data-vocabulary.org/# schema: http://schema.org/">
                        <div id="main" class="page-main-area" typeof="schema:Review">
                        <a id="main-content-area"></a> 
                        <main id="group-content" class="group group-content" >
                        <div id="page_title_content">
                           <h1 id="page-title" class="page-title title">HTC U11 review: HTC&#039;s flagship is a squeezy pleaser</h1>
                           <span property="schema:headline" content="HTC U11 review: HTC&#039;s flagship is a squeezy pleaser " class="rdf-meta element-hidden"></span>
                        </div>
                        <div id="content" class="region region-content content">
                        <div id="block-system-main" class="block block-system">
                        <div class="content">
                        <div class="node node-review odd node-full">
                        <div class="content">
                        <span property="schema:itemReviewed" content="HTC U11"></span>
                        <div class="field field-name-kicker field-label-inline">
                           <div class="field-items"><a href="/htc">HTC</a></div>
                        </div>
                        <h2 class="short-teaser" property="schema:description">Shiny but pricey; HTC once again falls into the Samsung comparison trap</h2>
                        <div class="field-group-format group_meta required-fields group-meta">
                           <span class="field field-name-field-author field-type-node-reference field-label-hidden">
                              <span class="field-item even" property="schema:author" typeof="schema:Person">
                                 <div class="node node-author node-sticky even node-inline-block" >
                                    <div class="content" >
                                       <div class="field field-name-field-author-first-name field-type-text field-label-hidden">
                                          <div class="field-items">
                                             <div class="field-item even"><span property="schema:name"><a href="http://www.alphr.com/authors/alan-martin" title="Alan Martin" class="author-link" property="schema:url">Alan Martin</a></span></div>
                                          </div>
                                       </div>
                                       <div class="field field-name-field-twitter-username field-type-text field-label-hidden">
                                          <div class="field-items">
                                             <div class="field-item even"><a href="http://www.twitter.com/alan_p_martin" class="follow-button-twitter" target="_blank" title="Follow on Twitter" rel="">@alan_p_martin</a></div>
                                          </div>
                                       </div>
                                    </div>
                                 </div>
                              </span>
                           </span>
                           <div class="field-name-field-published-date" ><span class="date-display-single" property="schema:datePublished" content="2017-07-12" datatype="xsd:dateTime">12 Jul 2017</span></div>
                        </div>
                        <div class="field field-name-field-review-score-overall field-type-fivestar field-label-hidden" property="schema:reviewRating" typeof="schema:Rating"><div class="field-items">
                            <div class="field-item even" property="schema:ratingValue" content="5"></div>
                        </div>
                        </body>
                    '''
        response = TextResponse(url='http://alphr.com/go/1006047', body=html_text)

        rdfa_items = extruct_helper.extract_all_rdfa(response)
        self.assertIsNotNone(rdfa_items)

        review = extruct_helper.get_review_items_from_rdfa(response, rdfa_items)
        self.assertEqual(len(review), 1)

        review = review[0]
        self.assertEqual(review['ProductName'], 'HTC U11')
        self.assertEquals(review['Author'], 'Alan Martin')
        self.assertEquals(review['TestDateText'], '2017-07-12')
        self.assertEquals(review['TestTitle'],
                          "HTC U11 review: HTC's flagship is a squeezy pleaser")
        self.assertEquals(review['TestSummary'],
                          'Shiny but pricey; HTC once again falls into the Samsung comparison trap')
