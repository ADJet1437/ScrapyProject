 
function check_alid_styler(value, row, index){
    if(value == 1){
        return 'background-color:green;color:white;';
    }else{
        return 'background-color:white;color:black;';
    }
}
function datagrid_filter_click(){
	var dg = $('#dg_alid_match').datagrid();
    enable_datagrid_filter(dg);
}

function enable_datagrid_filter(dg){
	var ft =  $('#id_filter_enabled').is(":checked");
	if(ft)
	    dg.datagrid('enableFilter',[
	            {field:'qa_approved',type:'numberbox',options:{precision:0},op:['equal','notequal']},
	            {field:'al_id',type:'numberbox',options:{precision:0},op:['equal','notequal','less','greater']},
	            {field:'testdate',type:'datebox',op:['equal','less','lessorequal','greater','greaterorequal']},
	            {field:'createtime',type:'datebox',op:['equal','less','lessorequal','greater','greaterorequal']},
	            {field:'level',type:'numberbox',options:{precision:0},op:['equal','notequal','less','greater']}
	                    ]);
	else
		dg.datagrid('disableFilter');
}
