# FdsPy
Projects using FactSet's APIs for data analysis

## [APIs](https://github.com/nurciuoli/FdsPy/tree/main/apis)
-  [__mypaengine__](https://github.com/nurciuoli/FdsPy/tree/main/apis/pa) - PA Engine API [(official documentation)](https://developer.factset.com/api-catalog/pa-engine-api)
-  [__myqengine__](https://github.com/nurciuoli/FdsPy/tree/main/apis/qe) - Quant Engine API [(official documentation)](https://developer.factset.com/api-catalog/quant-engine-api)
-  [__myspengine__](https://github.com/nurciuoli/FdsPy/tree/main/apis/spar) - SPAR Engine API [(official documentation)](https://developer.factset.com/api-catalog/spar-engine-api)
-  [__myfpe__](https://github.com/nurciuoli/FdsPy/tree/main/apis/fpe) - FactSet Programmatic Environment API [(official documentation)](https://developer.factset.com/api-catalog/factset-programmatic-environment-api)

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

## Analysis 
Specific projects utilizing these API Wrappers
- [__Fund Positioning__](https://github.com/nurciuoli/FdsPy/tree/main/analysis/Top%20Fund%20Positioning) - Analysis of how the top funds by AUM relative to specific indices are positioning
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/62541bf7-0494-4d49-8d1c-0a652f109d37)
- [__The Magnificent Seven Broker Estimates__](https://github.com/nurciuoli/FdsPy/tree/main/analysis/Broker%20Estimates) - Analysis of individual broker estimates for EPS have changed of the Magnificent 7
![image](https://github.com/nurciuoli/FdsPy/assets/57609455/bd4bc743-d0d3-448b-acf5-f499065a630e)
- [__Nvidia Holders__](https://github.com/nurciuoli/FdsPy/tree/main/analysis/Nvidia%20Holder%20Analysis) - Analysis of Mutual funds that current hold Nvidia



## Links
- __Official Analytics API SDK__ - https://github.com/factset/analyticsapi-engines-python-sdk
- __Developer Portal__ - https://developer.factset.com/
