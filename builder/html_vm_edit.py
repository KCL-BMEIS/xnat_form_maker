import time
## Bracnhing - this is redcap branching, not excell spreadhseets


def get_panel_name(input, tog_name):
    panel_name = 'panel{}'.format(tog_name)
    if 'panelNum' in input:
        panel_name = 'panel{}{}'.format(tog_name, input['panelNum'])
    return panel_name

def htmlTextString(input,el, out):
    iType = input['inputFormType']
    if 'subheader' in iType:
        print('SUBHEADER - {}'.format(input['question']))
        out.extend(editTypeSubHeader(input))
    elif 'eader' in iType:
        print('HEADER - {}'.format(input['question']))
        out.extend(editTypeHeader(input))
    elif 'insert' in iType:
        print('PARAGRAPH - {}'.format(input['question']))
        out.extend(editTypeHtml(input))
    elif 'paragraph' in iType:
        print('PARAGRAPH - {}'.format(input['question']))
        out.extend(editTypeParagraph(input))


def htmlInputEditStandard(input,el, out):

    iType = input['inputFormType']
    #print(iType)

    if 'branchingquestion' in input:
        out.extend(editTypeBranch(input, el, 'start'))

    if 'text' not in input['schemaInputType']:
        if iType != 'multiradio' and 'xstart' not in el:
            out.append('<tr>')
            out.append('<td valign="top" class="formLabel" style="white-space: normal;">{}</td>'.format(input['question']))
            out.append('  <td>')

    if 'branchVals' in input:
        #assumes radio....
        out.extend(editBranchToggle(input, el))

    elif iType == 'subform':
        out.extend(editTypeSubform(input, el))

    elif iType == 'multiradio':

        out.extend(editTypeMultiRadio(input, el))

    elif iType == 'radio':
        out.extend(editTypeRadio(input, el))

    elif iType == 'dropdown':
        out.extend(editTypeDropdown(input,el)) 
        
    elif iType == 'textarea':
        out.append(editTypeTextArea(el))

    elif iType == 'tickbox':
        out.append(editTypeTickBox(input, el))
    elif iType == 'date':
        out.append(editTypeDate(el))
    elif iType == 'datetime':
        out.append(editTypeDateTime(el))
    elif iType == 'time':
        out.append(editTypeTime(el))
    elif 'calc' in iType:
        print('CALC TYPE: {}'.format(input))
        out.append(editTypeCalc(input, el))
    elif 'text' in input['schemaInputType']:
            htmlTextString(input, el, out)
    else:
        out.append(editTypeText(input,el))

    out.append('  </td>')
    out.append('</tr>')

    if 'branchingquestion' in input:
        out.extend(editTypeBranch(input, el, 'end'))


def htmlInputEdit(input,schema,formRef, subform):
    out = []

    #print(input)    
    # Special types - shouldn't be here.....
    toggle_panels = ['ynuo','yn','ny','ynu', 'multipanel']


    el = '{}:{}/{}'.format(schema, formRef, input['dataName'])
    print('TEST EL, ',el, ' TEST EDIT TYPE,',input['inputFormType'])
    if subform:
        #must be subform, as includes main element:
        el = '@BASE_SCHEMA@/{}'.format(input['dataName'])

    iType = input['inputFormType']

    if 'x' in input['hide']:
        print('Skipping {} - hidden datatype'.format(input['dataName'], input['inputFormType']))
    elif iType in toggle_panels:
        print('Toggle panel....')
        out.extend(editTogglePanel(input,el))
    elif len(input['children']) > 0:
        print('{} - {} - has children...'.format(input['dataName'], input['inputFormType']))
        # check if toggle type with subs....

        elsub ='{}/{}'.format(el,input['subName'])
        htmlInputEditStandard(input, elsub, out)
        for i in input['children']:
            elsub = '{}/{}'.format(el, i['subName'])
            print('TEST SUB EL, ', elsub, ' TEST EDIT TYPE,', i['inputFormType'])
            if 'subheader' in i['inputFormType']:
                out.extend(editTypeSubHeader(i))
            elif 'header' in i['inputFormType']:
                out.extend(editTypeHeader(i))   
            elif 'aragraph' in i['inputFormType']:
                out.extend(editTypeParagraph(i))  
            elif i['inputFormType']   in toggle_panels:
                out.extend(editTogglePanel(i,elsub))
            else:
                htmlInputEditStandard(i, elsub, out)
        out.append('<tr><th><hr></th></tr>')
    else:
        htmlInputEditStandard(input,el, out)
        #print('{} - {}'.format(input['dataName'], input['inputFormType']))

    return out


def editTypeCalc(input, el):
    #schematype or inputtype?
    #return '#fmCalcType("{}" $item  $vr "{}")'.format(el, input['inputDataType'])
    #rounddown, sum, datediff,
    # datediff NOT from questions - they are entries in the same column!  And has formatting....
    #datediff - [date1,date2, dateformatting options]

    out=[]
    #datediff = dd
    if 'dd' in input['inputFormType']:

        #too complex
        #out.append('<input type="float" class="hidden" name="{}" id="{}">'.format(el,el))
        out  = editTypeText(input,el)
    elif 'sum' in input['inputFormType']:
        print('SUM, making hidden')
        out = '<input type="float" class="hidden" name="{}" id="{}">'.format(el,el)
    else:
        #if statment? just do text box for now
        out  = editTypeText(input,el)

    return out


def editTypeCalcJScript(input,schema,formRef):
    # this creates the javascript at the end
    # um datediff, can have rounddown and multiple complex datediffs, pluses and minuses

    el = '{}:{}/{}'.format(schema, formRef, input['dataName'])
    print('test JS: type:{}  '.format(input['inputFormType']))

    out=[]
    dtes = input['options'].split(' ')  #already split.... no commas, just spaces....

    if 'dd' in input['inputFormType']:
        print('test JS - datediff: sc:{}   fm:{}   in:{}'.format(schema, formRef, input))
        print(input['rawopts'])
        print('number of datediffs: {}'.format(input['rawopts'].count('datedif')))
        if input['rawopts'].count('datedif') == 1:

            if input['rawopts'].count(']') == 2:
                #simple datediff - sometime ],[, sometimes ], [
                aarr = input['rawopts'].replace('_','').replace(' ','').split('],[')
                dt1 = (aarr[0].split('['))[1]
                dt2 = (aarr[1].split(']'))[0]
                print('Found dates: {}   {} '.format(dt1, dt2))
                dt1 = '{}:{}/{}'.format(schema, formRef, dt1)
                dt2 = '{}:{}/{}'.format(schema, formRef, dt2)

                #time.sleep(2)
                # day, minutes, month etc
                format = 'd'
                if '"m"' in aarr[1]:
                    format = 'm'

                out.append('            calcDateDiff(\"{}\",\"{}\", \"{}\", \"{}\" )'.format(dt1,dt2,el, format))


    elif 'sum' in input['inputFormType']:
        print('test JS - sum: sc:{}   fm:{}   in:{}   dtes:{}'.format(schema, formRef, input, dtes))
        first = True
        for dt in dtes:
            a = dt.replace('datediff', '').replace('sum', '').replace(')', '')
            a = '{}:{}/{}'.format(schema, formRef, a.replace('_',''))
            if first:
                args = "[ \"{}\"".format(a)
                first = False
            else:
                args = "{},\"{}\"".format(args,a )
        args = '{} ]'.format(args)
        #sys.exit(0)
        #args = args.replace(' ',',{}:{}/'.format(schema, formRef))

        out.append("           calcSum(\"{}\", {})".format(el,args))
    return out



def editTypeHeader(input):
    head=[]
   
    head.append('<tr>')  
    head.append('<td style="align:left; font-weight: bold; font-size: 14px">{}</td>'.format(input['question']))            
    head.append('  <td>')
    head.append('  </td>')
    head.append('</tr>')  

    return head

def editTypeSubHeader(input):
    head=[]
   
    head.append('<tr>')  
    head.append('<td style="align:left; font-weight: bold; font-size: 12px">{}</td>'.format(input['question']))            
    head.append('  <td>')
    head.append('  </td>')
    head.append('</tr>')  

    return head



def editTypeHtml(input):
    head=[]
    head.append(input['question'])
    return head

def editTypeParagraph(input):
    head=[]
    head.append('<tr>')  
    head.append('<td style="align:left; font-size: 12px">{}</td><td></td>'.format(input['question']))
    head.append('</tr>')
    return head

def editTypeTickBox(input, el):
    default = 'n'
    if 'y' in input['options']:
        default='y'
    return '#fmBooleanCheckbox("{}" $item $vr "{}")'.format(el, default)

def editTypeTextArea(el):
    
    return '#xdatTextArea("{}" $item "" $vr 3 60)'.format(el)
    
def editTypeText(input,el):
    if "default" in input:
        return '#xdatTextBox("{}" $item "{}" $vr)'.format(el, input['default'])
    return '#xdatTextBox("{}" $item "" $vr)'.format(el)

def editTypeSubform(input, el):
    #format @BASE_ELEMENT@ @SUBFORM@ - repalced later on
    out = []
    out.append( '@{}@ @{}@'.format(el, input['options']))
    return out

def editTypeMultiRadio(input, el):
    #### so, see if string list. If so,
    #items = options = input['options'].split(',')
    out=[]
    options = input['options'].split(',')
    #print('# options, multiradio  {} - {}'.format(el, options))
    if len(input['options'])>0:
        out.append('    #set($list{}={})'.format(input['dataName'],options))
        out.append('    #renderfmStringMultiRadio("{}" $item $list{} $vr)'.format(el, input['dataName']) )

    return out


def editTypeRadio(input, el):
    #### so, see if string list. If so, 
    #items = options = input['options'].split(',')
    out=[]
    options = input['options'].split(',')
    if len(input['options'])>0:
        out.append('    #set($list{}={})'.format(input['dataName'],options)) 
        out.append('    #renderfmStringRadio("{}" $item $list{} $vr)'.format(el, input['dataName']) )
    else:
        out.append('    #fmRadioYesNo("{}" $item "0" $vr)'.format(el))
    return out

def editTypeDate(el):
    return '#fmDateBox("{}" $item $vr)'.format(el)
    #return '#xdatDatetBox("{}" $item $vr $years)'.format(el)


def editTypeDateTime(el):
    dtnum = el.replace(':','').replace('/','')
    return '#fmDateTimeBox("{}" $item $vr "{}")'.format(el, dtnum)
    #return '#fmDateTimeLocalBox("{}" $item $vr )'.format(el)


def editTypeTime(el):
    dtnum = el.replace(':','').replace('/','')
    return '#fmTimeBox("{}" $item $vr "{}")'.format(el, dtnum)



def editTypeDropdown(input,el):

    out = []
    # should be comma del by the time you get here
    
    options = []
    print('#### DROPDOWN {} - {}'.format(input['inputDataType'], input['options']))
    #RANGE SAVED AS STRING
    if input['inputLen']>0:
        # if inputlen, then save as int.
        for i in range(0,int(input['inputLen']) + 1 ):
            options.append("{}".format(i))
        out.append('                            #set($list{}={})'.format(input['dataName'],options)) 
        out.append('                            #renderfmIntegerDropdown( "{}" $item $list{}  $vr)'.format(el,input['dataName']))
    elif 'tring' in input['inputDataType']:
        if ',' not in input['options'] and '-' in input['options']:
            #saved as string
            options = []
            opts_range = input['options'].split('-')

            try:
                min_opt = int(opts_range[0])
                max_opt = int(opts_range[1])
                for i in range(min_opt, max_opt + 1):
                    options.append("{}".format(i))
            except ValueError as ve:
                options.append(input['options'])


        else:
            options = input['options'].split(',')
        out.append('                            #set($list{}={})'.format(input['dataName'],options))
        if "default" in input:
            out.append('                            #renderfmStringDropdown("{}" $item $list{} "{}"  $vr)'.format(el,input['dataName'],input['default']))
        else:
            out.append('                            #renderfmStringDropdown("{}" $item $list{} ""  $vr)'.format(el,input['dataName']))
    else:
        options = input['options'].split(',')
        #out.append('                            #renderfmStringDropdown("{}" $item $list{}  $vr)'.format(el,input['dataName']))
        out.append('                            #set($list{}={})'.format(input['dataName'],options))
        out.append('                            #renderfmScalarPropertySelect("{}" $item $list{}  $vr)'.format(el,input['dataName']))
    return out






def editTypeBranch(input, el, section):
    out = []

    tog_name = (input['branchingquestion'].split(':')[1]).replace('/', '').replace('_', '')
    panel_name = get_panel_name(input, tog_name)
    if 'start' in section:
        out.append('</table>')
        out.append('      #set (${} = $!item.getProperty("{}"))'.format(tog_name, input['branchingquestion']))
        out.append('<table id="{}" class="#if(${} == "{}")unhidden#{{else}}hidden#end">'.format(panel_name, tog_name, input['branchingvalue']))
    else:
        out.append('</table>')
        out.append('<table>')
    return out

def editBranchToggle(input, el):
    #generic macro - fmGenericStringToggle $name $item $items $default $panel $vals $vr)
    #    numbers each value
    iType = input['inputFormType']
    out =[]
    tog_name = (el.split(':')[1]).replace('/', '').replace('_', '')

    options = input['options'].split(',')
    vals = ','.join(input['branchVals'])

    if 'default' not in input:
        default = ''
    else:
        default = input['default']

    if 'ynredcap' in iType:
        out.append('                            #fmRedcapBoolToggle("{}"  "{}" "panel{}" "{}" $vr)'.format(el, default, tog_name, vals))

    else:
        out.append('                            #set($list{}={})'.format(input['dataName'], options))
        out.append('                            #fmGenericStringToggle("{}" $item $list{} "{}" "panel{}" "{}" $vr)'.format(el, input['dataName'], default, tog_name, vals))
        print('TOGGLE #fmGenericStringToggle("{}" $item $list{} "{}" {} "{}" $vr)'.format(el,input['dataName'],default,tog_name,vals))
        #time.sleep(2)
        #os.exit(0)
    return out


def editTogglePanel(input,el):
    
    out =[]
    iType = input['inputFormType']
    if 'multipanel' in iType:
        #count number of yes, then split later....
        opts = input['options'].replace(';','').replace(',','').replace('=','').rstrip()
        qs = opts.split('N')
        #print('options: {}  '.format(qs))
        yes_qs = int(qs[0].replace('Y',''))
        no_qs = int(qs[1].replace('N',''))
        #print('{}  y:{}   n:{} '.format(qs, yes_qs, no_qs))
    tog_name = '{}{}'.format(input['formRef'], input['dataName'])
    if input['subName'] != '':
        tog_name = '{}{}'.format(tog_name, input['subName'])
        el = '{}/{}'.format(el, input['subName'])

    panel_name = get_panel_name(input, tog_name)

    #("toggle type: element:{}   -  {}".format(el, input))
    out.append('<tr>')  
    out.append('    <td valign="top" class="formLabel">{}</td>'.format(input['question']))
    out.append('    <td>')

    if 'ynuo' in iType:
        out.append('                             #fmRadioYesNoUnableOtherTogglePanel("{}/completed" $item "{}" $vr)'.format(el, panel_name))
        out.append('                                 #set (${} = $!item.getProperty("{}/completed"))'.format(tog_name, el))

        out.append('                                 <table id="{}" class="#if(${} == "3")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name) )
        out.append('                                     #getUnableCategories()')
        out.append('                                     <TR><TD>Reason for not completing:</TD><TD>#renderfmScalarPropertySelect("{}/reasonNotAble" $item $unableCategories $vr)</TD></TR>'.format(el) )
        out.append('                                 </table>')
    elif 'ny' in iType:
        out.append('                             #fmRadioNoYesToggle("{}" $item 0 "{}" $vr)'.format(el, panel_name))
        out.append('                                 #set (${} = $!item.getProperty("{}"))'.format(tog_name, el))
    elif 'multipanel' in iType:
        out.append('                                 #fmRadioYesNoBothToggle("{}" $item 0 "{}Y" "{}N" $vr)'.format(el, panel_name,  panel_name))
        out.append('                                 #set (${} = $!item.getProperty("{}"))'.format(tog_name, el))
    else:
        out.append('                             #fmRadioYesNoToggle("{}" $item 0 "{}" $vr)'.format(el, panel_name))
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
                    htmlInputEditStandard(c, el, childRowsY)
                else:
                    htmlInputEditStandard(c, el, childRowsN)
                ii += 1

        else:
            for c in input['children']:
                el='{}:{}/{}/{}'.format(c['schema'],c['formRef'],input['dataName'],c['subName'])
                htmlInputEditStandard(c,el, childRows)
                #print('adding child rows to toggle panel:{} {} {} {}'.format(el, c['subName'],c['schema'],c['formRef']) )
    if len(childRows) > 0 and 'ynuo' in iType:
        out.append('                                 <table id="{}Y" class="#if(${} == "1")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRows)
        out.append('                                 </table>')
    elif len(childRows) > 0 and 'yn' in iType:
        out.append('                                 <table id="{}" class="#if(${} == "1")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRows)
        out.append('                                 </table>')
    if len(childRows) > 0 and 'ny' in iType:
        out.append('                                 <table id="{}" class="#if(${} == "0")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRows)
        out.append('                                 </table>')
    if len(childRowsY) > 0 and 'multip' in iType:
        out.append('                                 <table id="{}Y" class="#if(${} == "1")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRowsY)
        out.append('                                 </table>')
        out.append('                                 <table id="{}N" class="#if(${} == "0")unhidden#{{else}}hidden#end">'.format(panel_name,tog_name)  )
        out.extend(childRowsN)
        out.append('                                 </table>')
    out.append('    </td>')
    out.append('</tr>')

    return out



def cleanForm(out):
    ln = 0
    for line in out:
        if ln > 0:
            if out[ln] == out[ln-1]:
                if '<tr><th><hr></th></tr>' in out[ln]:
                    del out[ln]
        ln = ln +1
    return out