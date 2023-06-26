def get_panel_name(input, tog_name):
    panel_name = 'panel{}'.format(tog_name)
    if 'panelNum' in input:
        panel_name = 'panel{}{}'.format(tog_name, input['panelNum'])
    return panel_name

def htmlTextString(input,el, out):
    iType = input['inputFormType']
    # print('Test Report: {}'.format(input))
    if 'subheader' in iType:
        print('REPORT-SUBHEADER: {} - {} '.format(input['question'], input['inputFormType']))
        out.extend(reportTypeSubHeader(input))
    elif 'eader' in iType:
        print('REPORT-HEADER: {} - {} '.format(input['question'], input['inputFormType']))
        out.extend(reportTypeHeader(input))
    elif 'aragraph' in iType:
        print('REPORT-PARAGRAPH: {} - {} '.format(input['question'], input['inputFormType']))
        out.extend(reportTypeParagraph(input))


def htmlInputReportStandard(input,el, out):
    dType = ""
    if input['inputDataType']:
        dType = input['inputDataType']
    iType = input['inputFormType']
    if 'text' in input['schemaInputType']:
        htmlTextString(input, el, out)

    else:
        if 'branchingquestion' in input:
            # only show if....
            out = reportTypeBranch(input, out)
        else:
            out.append('<tr>')
        
        out.append('<td valign="top" class="formLabel"  style="white-space: normal;">{}</td>'.format(input['question']))

        out.append('<td valign="top">')

        if iType == 'radio':
            out.append(reportTypeRadio(input, el))

        elif iType == 'subform':
            out.extend(reportTypeSubform(input, el))

        elif iType == 'dropdown' and dType == 'int':
           
            out.extend(reportTypeDropdown(input,el))

        elif iType == 'tickbox':
            out.append(reportTypeTickBox(el))

        elif iType == 'date':
            out.append(reportTypeDateBox(el))

        elif iType == 'datetime':
            out.append(reportTypeDateTimeBox(el))

        elif iType == 'ynredcap':
            #just shows boolean
            out.append(reportTypeTickBox(el))

        else:
            out.append(reportTypeText(el))

        out.append('</td>')
        out.append('</tr>')

def htmlInputReport(input,schema,formRef, subform):
    toggle_panels = ['ynuo','yn','ny','ynu', 'multipanel']
    out =[]

    el='{}:{}/{}'.format(schema,formRef,input['dataName'])
    if subform:
        #must be subform, as includes main element:
        el = '@BASE_SCHEMA@/{}'.format(input['dataName'])

    iType = input['inputFormType']

    if 'x' in input['hide']:
        print('Skipping {} - {} - hidden datatype'.format(input['dataName'], input['inputFormType']))
    elif iType in toggle_panels:
        out.extend(reportTogglePanel(input,el))
    elif len(input['children']) > 0:
        elsub='{}/{}'.format(el,input['subName'])
        htmlInputReportStandard(input, elsub, out)        
        for i in input['children']:
            print('REPORT-test: {}'.format(i))
            elsub ='{}/{}'.format(el,i['subName'])
            if 'subheader' in i['inputFormType']:
                print('SUB: REPORTSUBHEADER  {}'.format(i['question']))
                out.extend(reportTypeSubHeader(i)) 
            elif 'eader' in i['inputFormType']:
                print('SUB: REPORTHEADER {}'.format(i['question']))
                out.extend(reportTypeHeader(i)) 
            elif  'aragraph' in i['inputFormType']:
                print('SUB: REPORT PARAGRAPH {}'.format(i['question']))
                out.extend(reportTypeParagraph(i)) 
            elif i['inputFormType'] in toggle_panels:
                out.extend(reportTogglePanel(i,elsub))
            else:
                htmlInputReportStandard(i, elsub, out)
        out.append('<tr><th><hr></th></tr>')  
    else:
        htmlInputReportStandard(input, el, out) 


    return out

def reportTypeHeader(input):
    head=[]

    head.append('<tr>')  
    head.append('<td style="align:left; font-weight: bold; font-size: 14px">{}</td>'.format(input['question']))            
    head.append('  <td>')
    head.append('  </td>')
    head.append('</tr>')  

    return head



def reportTypeSubHeader(input):
    head=[]

    head.append('<tr>')  
    head.append('<td style="align:left; font-weight: bold; font-size: 12px">{}</td>'.format(input['question']))            
    head.append('  <td>')
    head.append('  </td>')
    head.append('</tr>')  

    return head


def reportTypeBranch(input, out):
    tog_name = input['branchingquestion'].replace('/', '').replace(':', '').replace('_', '')
    out.append(' #set (${} = $!item.getProperty("{}"))'.format(tog_name, input['branchingquestion']))
    out.append('<tr style="#if(${} == "{}")all#{{else}}display:none;#end">'.format(tog_name, input['branchingvalue']))
    return out

def reportTypeParagraph(input):
    out=[]

    if 'branchingquestion' in input:
        out = reportTypeBranch(input, out)
    else:
        out.append('<tr>')
    out.append('<td style="align:left; font-size: 12px">{}</td>'.format(input['question']))
    out.append('</tr>')

    return out

def reportTypeSubform(input, el):
    #format @BASE_ELEMENT@ @SUBFORM@ - repalced later on
    out = []
    out.append('@{}@ @{}@'.format(el, input['options']))
    return out

def reportTypeDateTimeBox(el):
    return '#showDateTime("{}" $item)'.format(el)

def reportTypeDateBox(el):
    return '#showDate("{}" $item)'.format(el)


def reportTypeTickBox(el):
    
    return '#showfmBoolean("{}" $item)'.format(el)

def reportTypeText(el):

    return '$!item.getStringProperty("{}")'.format(el)

def reportTypeRadio(input, el):
    if len(input['options'])>0:
        return '                            $!item.getProperty("{}")'.format(el)
    else:
        return '#showfmBoolean("{}" $item)'.format(el)


def reportTypeDropdown(input,el):

    out = []
    options = []


    if input['inputLen'] > 0:
        # then take from length
        for i in range(0, int(input['inputLen']) + 1):
            options.append("{}".format(i))
    else:
        if ',' not in input['options'] and '-' in input['options']:
            #saved as string
            opts_range = input['options'].split('-')
            min_opt= int(opts_range[0])
            max_opt= int(opts_range[1])
            for i in range(min_opt, max_opt + 1):
                options.append("{}".format(i))
        else:
            options = input['options'].split(',')



    print(options,el,input['dataName'])
    if 'nt' not in input['inputDataType']:
        out.append('                            $!item.getProperty("{}")'.format(el) )
    else:
        out.append('                             #set($list{}={})'.format(input['dataName'],options))                
        out.append('                             #showScalarIntProperty("{}" $item $list{} )'.format( el,input['dataName']))
    return out
    

def reportTogglePanel(input,el):
   
    out =[]
    iType = input['inputFormType']
    if 'multipanel' in iType:
        #count number of yes, then split later....
        opts = input['options'].replace(';','').replace(',','').replace('=','')
        qs = opts.split('N')
        print('options: {}  '.format(qs))
        yes_qs = int(qs[0].replace('Y',''))
        no_qs = int(qs[1].replace('N',''))
        print('{}  y:{}   n:{} '.format(qs, yes_qs, no_qs))

    tog_name = '{}{}'.format(input['formRef'],input['dataName'])
    if input['subName'] != '':
        tog_name = '{}{}'.format(tog_name,input['subName'])
        el = '{}/{}'.format(el, input['subName'])
   
    panel_name = get_panel_name(input, tog_name)
    print("toggle type: element:{}   -  {}".format(el, input))
    out.append('<tr>')  
    out.append('<td valign="top" class="formLabel">{}</td>'.format(input['question']))  
    out.append('    <td>')  
    
    if 'ynuo' in iType:
        out.append('                            #showNoYesUnableOther("{}/completed" $item "{}" $vr)'.format(el, panel_name))
        out.append('                                 #set (${} = $!item.getProperty("{}/completed"))'.format(tog_name, el))

        out.append('                                 <table id="{}" class="#if(${} == "3")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name) )
        out.append('                                     <tr><td>Reason for not completing:</td><td> #showReasonUnable("{}/reasonNotAble" $item)</td></tr>'.format(el))
        out.append('                                 </table>')
    else:
        out.append('                             #showYesNo("{}" $item "{}")'.format(el, panel_name))    
        out.append('                                 #set (${} = $!item.getProperty("{}"))'.format(tog_name, el))

    childRows = []
    childRowsY = []
    childRowsN = []
    #if  i have children, all for answer yes at the moment
    if len(input['children']) > 0:
        if 'multipanel' in iType:
            ii = 0
            for c in input['children']:
                el = '{}:{}/{}/{}'.format(c['schema'], c['formRef'], input['dataName'], c['subName'])
                if ii < yes_qs:
                    htmlInputReportStandard(c,el, childRowsY)
                else:
                    htmlInputReportStandard(c,el, childRowsN)
                ii += 1

        else:
            for c in input['children']:
                el='{}:{}/{}/{}'.format(c['schema'],c['formRef'],input['dataName'],c['subName'])
                htmlInputReportStandard(c,el, childRows)
                print('adding child rows to report panel:{} {} {} {}'.format(el, c['subName'],c['schema'],c['formRef']) )
                #childRows.extend(htmlInputReport(c,c['schema'],c['formRef']))
    print('itype: {} childRowsN {}'.format(iType, childRowsN))
    if len(childRows) > 0 and 'yn' in iType:
        out.append('                                 <table id="{}1" class="#if(${} == "1")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRows)
        out.append('                                 </table>')
    if len(childRows) > 0 and 'ny' in iType:
        out.append('                                 <table id="{}1" class="#if(${} == "0")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRows)
        out.append('                                 </table>')
    if len(childRowsY) > 0 and 'multip' in iType:
        out.append('                                 <table id="{}Y" class="#if(${} == "1")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRowsY)
        out.append('                                 </table>')
        out.append('                                 <table id="{}N" class="#if(${} == "0")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRowsN)
        out.append('                                 </table>')

    out.append('</td></tr>')

    return out
