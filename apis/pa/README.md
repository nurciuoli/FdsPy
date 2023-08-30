# mypaengine

## PA Document Inputs Reference
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/49b97eaf-fd0c-4ecd-922f-038ff453b0a8)

## Classes & Methods
### 1. Document Template Class
```python
class DocumentTemplate:
    def __init__(self,component_id=None,
                    pa_document_name = None,
                    pa_component_category = None,
                    pa_component_name = None,**kwargs):
        if(component_id==None):
            self.component_id = find_component_id(pa_document_name,pa_component_category,pa_component_name)
        else:
            self.component_id = component_id
        self.root= None
        self.data = None
    def __str__(self):
        return self
```
#### Example: Defining a DocumentTemplate object using names
```python
pa_doc = pa.DocumentTemplate(pa_document_name = "PERSONAL:API_REPORTS_SINGLE",
                    pa_component_category = "main / 3 Factor Attribution",
                    pa_component_name = "3 Factor Attribution",
                    )
```
####  Defining a DocumentTemplate object using component id
```python
pa_doc =pa.DocumentTemplate(component_id = 'B69AD8072581C52409DC1B8ED094308F42981653140698A0A0DE9509746DF98D')
```
#### Run Calc Method
```python
  def run_calc(self,
                portfolios,
                benchmarks,
                start_date = None,
                end_date = '0',
                frequency = 'Single',
                curr = 'USD',
                mode= 'B&H',
                componentdetail = "SECURITIES",
                **kwargs):
```
#### Example: Running Calculation
```python
pa_doc.run_calc(
               ['LION:SPY-US','LION:IVV-US'],
               ['BENCH:SP50','BENCH:SP50'],
               start_date = '20221230',
               end_date = '0M',
               frequency = 'Monthly',
               curr = 'USD',
               mode= 'B&H'
              )
```
### Output
#### Example: Calling Data Attribute
```python
pa_doc.data
```
##### Result
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/7cec6b76-2c7f-4a5b-9c5a-37ff10eac28b)
#### Example: Calling Root Attribute
```python
pa_doc.root
```
##### Result
```
{'data': {'LION:IVV-US_x_BENCH:SP50': {'accounts': [{'holdingsmode': 'B&H', 
                                                     'id': 'LION:IVV-US'}],
                                       'benchmarks': [{'holdingsmode': 'B&H',
                                                       'id': 'BENCH:SP50'}],
                                       'componentdetail': 'SECURITIES',
                                       'componentid': 'B69AD8072581C52409DC1B8ED094308F42981653140698A0A0DE9509746DF98D',
                                       'currencyisocode': 'USD',
                                       'dates': {'enddate': '-1M',
                                                 'frequency': 'Single',
                                                 'startdate': '-2M'}},
          'LION:SPY-US_x_BENCH:SP50': {'accounts': [{'holdingsmode': 'B&H',
                                                     'id': 'LION:SPY-US'}],
                                       'benchmarks': [{'holdingsmode': 'B&H',
                                                       'id': 'BENCH:SP50'}],
                                       'componentdetail': 'SECURITIES',
                                       'componentid': 'B69AD8072581C52409DC1B8ED094308F42981653140698A0A0DE9509746DF98D',
                                       'currencyisocode': 'USD',
                                       'dates': {'enddate': '-1M',
                                                 'frequency': 'Single',
                                                 'startdate': '-2M'}}}}
```


### 2. Unlinked Template Calculation
```python
def calc_unlinked_template(portfolios= ["LION:IVV-US"],
                                            benchmarks = ["DEFAULT"],
                                            start_date = None,
                                            end_date = "0D",
                                            template_type_name= 'Weights',
                                            columns = [{'name' : "Port. Ending Weight",'category':"Portfolio/Position Data",'directory' :"Factset"}],
                                            stats =["Weighted Average"],
                                            level = 'SECURITIES',
                                            groups = [{'name' : None,'category':None,'directory' :None}],
                                            holdings_mode = "B&H",
                                            report_frequency = 'Single',
                                            **kwargs):
```

#### Example: Running Unlinked Template
```python
pa.calc_unlinked_template(columns =[{'name' : "Port. Ending Weight",'category' : "Portfolio/Position Data","directory":"Factset"},
                                            {"name":"Port. Ending Price","category":"Prices/Portfolio","directory":"Factset"},
                                            {"name":"Port. Ending Quantity","category":"Portfolio/Position Data","directory":"Factset"}],
                        groups=[{"name":'RBICS Focus - Economy',"category":'Sector & Industry/FactSet - RBICS/RBICS Focus',"directory":'Factset'}],
                        end_date ='0M',
                        portfolios=['LION:QQQ-US']
                        )
```


## Links
-  Official SDK: https://github.com/factset/analyticsapi-engines-python-sdk
-  Official Documentation: https://developer.factset.com/api-catalog/pa-engine-api
