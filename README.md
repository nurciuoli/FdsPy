# FdsPy
Custom wrappers using FactSet's APIs for data analysis

## [Modules](https://github.com/nurciuoli/FdsPy/tree/main/FdsPy)
- PA (Portfolio Analysis)
  - [__mypaengine__](https://github.com/nurciuoli/FdsPy/tree/main/apis/pa) - PA Engine API [(official documentation)](https://developer.factset.com/api-catalog/pa-engine-api)
  - utils
- QE (Quant Engine)
  - [__myqengine__](https://github.com/nurciuoli/FdsPy/tree/main/apis/qe) - Quant Engine API [(official documentation)](https://developer.factset.com/api-catalog/quant-engine-api)
  - utils
- SPAR
  - [__myspengine__](https://github.com/nurciuoli/FdsPy/tree/main/apis/spar) - SPAR Engine API [(official documentation)](https://developer.factset.com/api-catalog/spar-engine-api)
- FPE (FactSet Programmatic Environment)
  - [__myfpe__](https://github.com/nurciuoli/FdsPy/tree/main/apis/fpe) - FactSet Programmatic Environment API [(official documentation)](https://developer.factset.com/api-catalog/factset-programmatic-environment-api)
  - utils
- Misc
  - utils
    - Google Trends
    - Fred API 

## Setup
### Requirements
- __Packages Required__ - [pip install fds.analyticsapi.engines](https://pypi.org/project/fds.analyticsapi.engines/)
- __Authentication__ - generate API Key & whitelist IP address (or address range) at the [Developer Portal](https://developer.factset.com/)
### Environment Variables
- __FACSET_USERNAME__ - Username & Serial (ex. FDS_US_DEMO-123842)
- __FACTSET_API_KEY__ - accessed via developer portal

## Screenshots
### mypaengine
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/8aee2651-fec8-4d94-9ba5-d15a58d0a231)
-----------------
### myqengine
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/59f974f0-7ead-42c5-9d06-fdb55b1789ee)
-----------------
### myspengine
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/08b69ef9-ad23-49da-b3b2-4e1284de299e)
------------------
### myfpe
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/96ef46aa-96b1-4fde-9765-588cf97d4198)

## [Analysis](https://github.com/nurciuoli/MyProjects/tree/main)
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/62541bf7-0494-4d49-8d1c-0a652f109d37)
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/bd4bc743-d0d3-448b-acf5-f499065a630e)


## Links
- __Official Analytics API SDK__ - https://github.com/factset/analyticsapi-engines-python-sdk
- __Developer Portal__ - https://developer.factset.com/
