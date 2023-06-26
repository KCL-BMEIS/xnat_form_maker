# if schmea type = text, then ignores (this includes header, subheader etc.
import errno
import os

class SchemaHandler(object):

    def __init__(self, configData):

        self.errors = []
        self.log =[]
        self.configData = configData
        self.schemaName = configData['schemaName']
        self.version = configData['version']

        self.part_plugin_path = 'src/main/resources/schemas'

    def hasError(self):
        return len(self.errors)

    def errors(self):
        return self.errors
    
    
    def checkDir(self,vmFile):

        if not os.path.exists(os.path.dirname(vmFile)):
          try:
              os.makedirs(os.path.dirname(vmFile))
          except OSError as exc: # Guard against race condition
              if exc.errno != errno.EEXIST:
                  raise

    def write_schema_xsd(self,plugin_name,data):
 
      
      dir_name = '{}/plugins/{}/{}/{}'.format(self.configData['path_plugin_builder'],self.schemaName,self.part_plugin_path,self.schemaName)
      schema_file = '{}/{}.xsd'.format(dir_name,self.schemaName)

      self.log.append('write schema dir : {}'.format(dir_name))
      self.log.append('write schema file : {}'.format(schema_file))

      if not os.path.exists(dir_name):
        os.makedirs(dir_name)

      #lets load our [replace me] template        
      fxsd = open(schema_file,"w")   
      for line in data:
        fxsd.write(line + '\n')
      fxsd.close()

    def all_data_xsd(self,data):
        #print(data)
        out = self.schemaHeader()

        #add all form xml elments -DO SUBFORMS FIRST
        for f in data['forms']:
            if 'subform' in data['forms'][f]['ext']:
                print('SUBFORM', data['forms'][f]['ext'])
                out.extend(self.formXsd(data['forms'][f]))


        for f in data['forms']:
            if 'subform' not in data['forms'][f]['ext']:
                print('NOT SUBFORM', data['forms'][f]['ext'])
                out.extend(self.formName(data['forms'][f]))
        #os.exit()

        out.append(' ')
        out.append(' ')
        out.append(' ')

        for f in data['forms']:
            if 'subform' not in data['forms'][f]['ext']:
                out.extend(self.formXsd(data['forms'][f]))

        out.extend(self.end_schema())

        return out

    def formXsd(self,form):

        out =[]

        out.extend(self.start_complex_type_named(form['ref']))

        #not used
        out.extend(self.make_form_desc(form['name']))
        if 'subform' not in form['ext']:
            out.extend(self.start_complex_content())
            #not for subforms as do not extend
            s = 'imageAssessorData'
            if 'ubj' in form['ext']:
                s = 'subjectAssessorData'
            out.extend(self.start_extension(s))

        out.extend(self.start_sequence())

        out.extend(self.make_form_inputs(form))

        out.extend(self.end_sequence())
        if 'subform' not in form['ext']:
            out.extend(self.end_extension())
            out.extend(self.end_complex_content())

        out.extend(self.end_complex_type())
        
        out.append(' ')
        out.append(' ')
        out.append(' ')
        return out


    def schemaHeader(self):

      host = self.configData['host']

      if not host.endswith('/'):
          host = '{}/'.format(host)
   
      out = []

      out.append('<xs:schema targetNamespace="{}{}"'.format( host, self.schemaName) )
      out.append('xmlns:{}="{}{}"'.format(  self.schemaName, host, self.schemaName ) )
      out.append('xmlns:xs="http://www.w3.org/2001/XMLSchema"')
      out.append('elementFormDefault="qualified"')
      out.append('attributeFormDefault="unqualified"')
      #xdat Not in 1.8
      if '17' in self.version:
          out.append('xmlns:xdat="http://nrg.wustl.edu/xdat"')
      out.append('xmlns:xnat="http://nrg.wustl.edu/xnat">')
      out.append('<xs:import namespace="http://nrg.wustl.edu/xnat" schemaLocation="../xnat/xnat.xsd"/>')
      out.append(' ')
      out.append(' ')
      out.append(' ')
      #out.extend(self.addAssessCompleted())
      
      return out


    def addAssessCompleted(self):

      out =[]
      
      out.append(' <xs:complexType name="assess_completed">')
      out.append('       <xs:sequence>')
      out.append('     <xs:element name="completed" minOccurs="0">')
      out.append('                <xs:simpleType>')
      out.append('                 <xs:restriction base="xs:integer"/>')
      out.append('              </xs:simpleType>')
      out.append('             </xs:element>')
      out.append('             <xs:element name="reasonNotAble" minOccurs="0">')
      out.append('              <xs:simpleType>')
      out.append('                     <xs:restriction base="xs:integer"/>')
      out.append('              </xs:simpleType>')
      out.append('             </xs:element>')
      out.append('     </xs:sequence> ')
      out.append(' </xs:complexType>')
      out.append(' ')
      out.append(' ')
      out.append(' ')
      return out


    def formName(self,form):
       
       out = []
       if 'subform' not in form['ext']:
           out.append('  <xs:element name="{}Assessment" type="{}:{}"/>'.format( form['ref'], self.schemaName,form['ref']) )
       return out

    def make_form_desc(self,formDesc):
       
      out = []
      #out.append('    <xs:annotation>')
      #out.append('        <xs:documentation>{}</xs:documentation>'.format(formDesc) )
      #out.append('     </xs:annotation>')
      return out


    def make_form_inputs(self,form):
       
      out = []
      doneDataNames = []

      for i in form['inputs']:
        

        dataName = i['dataName']
        self.log.append('   DATANAME: {} - {}'.format(dataName, i['inputFormType']))
        if 'text' in i['schemaInputType']:
          self.log.append('Skipping as header or paragraph - {}'.format(i['question']))
        elif len(i['children']) > 0:
          # self.log.append(' create group {}, form type : {} , datatype : {}'.format(i['dataName'],  i['inputFormType'],i['schemaInputType']))
          
          self.log.append('   Group input :  {}'.format(i['dataName']))
          self.log.append('      -- Group input :  {}'.format(i['question']))
          out.extend(self.make_complex_inputs(dataName,i))

        else:
            self.log.append('   non - group input :  {}'.format(i['question']))
            #### if restriction""""
            
            if i['inputLen'] > 0:
                out.extend(self.input_restrict(dataName,i))
            else:
                out.extend(self.input_default(dataName,i))
  
      return out


    def make_complex_inputs(self,dataName,input):
      # self.traverse(input)
      out = []
      out.append('<xs:element name="{}">'.format(input['dataName']))
      out.extend(self.start_complex_type())
      out.extend(self.start_sequence())

      out.extend(self.input_default(input['subName'], input))

      for i in input['children']:
          self.log.append('      -- Group input :  {}'.format(i['question']))

          if 'text' not in i['schemaInputType']:
              if i['inputLen'] > 0:
                  out.extend(self.input_restrict(i['subName'],i))
              else:
                  out.extend(self.input_default(i['subName'], i))

      out.extend(self.end_sequence())
      out.extend(self.end_complex_type())
      
      out.append('</xs:element>')

      return out


    def input_restrict(self,elName,data):

      out = []
      
      out.append('        <xs:element name="{}" minOccurs="{}" maxOccurs="1">'.format(elName, data['required'] ))
      out.extend(self.input_question(data['question']) )     
      out.append('              <xs:simpleType>')
      out.append('                    <xs:restriction base="xs:{}">'.format( data['schemaInputType']) )
      if 'tring' in data['schemaInputType']:
          out.append('                        <xs:maxLength value="{}"/>'.format( data['inputLen']) )
      else:
          out.append('                         <xs:minInclusive value="0"/>')
          out.append('                          <xs:maxInclusive value="{}"/>'.format( data['inputLen']) )
      out.append('                    </xs:restriction>')
      out.append('            </xs:simpleType>')
      out.append('        </xs:element>') 

      return out

    def input_default(self,elName,data):
      
      if data['inputFormType'] == 'ynuo' :
        return self.input_ynuo(elName)

      out = []
      if 'text' not in data['schemaInputType']:
          if 'subform' in data['inputFormType']:
              out.append('      <xs:element name="{}" type="{}:{}" minOccurs="{}">'.format(elName, self.schemaName, data['schemaInputType'], data['required']))
          else:
              out.append('      <xs:element name="{}" type="xs:{}" minOccurs="{}">'.format(elName,data['schemaInputType'], data['required'] ))
          out.extend(self.input_question(data['question']) )
          out.append('      </xs:element>')
      return out

    def input_ynuo(self,elName):
      out = []
      out.append('     <xs:element name="completed" minOccurs="0">')
      out.append('                <xs:simpleType>')
      out.append('                 <xs:restriction base="xs:integer"/>')
      out.append('              </xs:simpleType>')
      out.append('             </xs:element>')
      out.append('             <xs:element name="reasonNotAble" minOccurs="0">')
      out.append('              <xs:simpleType>')
      out.append('                     <xs:restriction base="xs:integer"/>')
      out.append('              </xs:simpleType>')
      out.append('             </xs:element>')
      return out
       #return ['        <xs:element name="{}" type="{}:assess_completed" minOccurs="0"/>\n'.format(elName,self.schemaName)]

    def input_question(self,q):
       
      out = []

      #out.append('        <xs:annotation>')
      #out.append('          <xs:documentation>{}</xs:documentation>'.format(q) )
      #out.append('        </xs:annotation>')
      return out


    def end_schema(self,):
       
       return ['</xs:schema>']

    def start_complex_type(self):
       
       return ['<xs:complexType>']

    def start_complex_type_named(self,name):
       
       return ['<xs:complexType name="{}">'.format( name)]

    def end_complex_type(self):

       
       return ['</xs:complexType>']

    def start_complex_content(self):

       return ['<xs:complexContent>']

    def end_complex_content(self):

       return ['</xs:complexContent>']

    def start_extension(self,e):

    	return ['<xs:extension base="xnat:{}">'.format(e)]

    def end_extension(self):

       return ['</xs:extension>']

    def start_sequence(self):

       return ['<xs:sequence>']

    def end_sequence(self):

       return ['</xs:sequence>']