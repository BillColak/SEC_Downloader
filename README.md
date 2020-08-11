# SEC_Downloader
This code allows you to download SEC financial statements as pandas dataframes and converts it into Excel SpreadSheets.
If you have any suggestions on how to improve this project or would like to contribute please let me know.

Why use this code
------------
- By implementing XBRL validation, this code can be used for data mining and mass downloading of SEC filings.
- This code provides more freedom to developers as it does not depend on third party data providers.
- This code does not break as easily as other open source code out there. If you do come across some issues please let me know.

- Thanks and firm hand shakes.

Screenshots
-----------

![](images/image1.png)

![](images/image2.png)

How-to's
-----------
- download to excel: type the ticker of interest and the file-type your are looking for (10-K, 10-Q, 40-F).

How does it work
-----------
- The get_sec_file function returns a dictionary with urls of the financial statements, which gets scraped and parsed by the parse_sec_file function. 
- By default get_sec_file function returns all five IS, BS, CF, EQ, CI financial statements as pandas dataframas. Here you can implement your own methods.

Requirements
------------
- requests==2.24.0
- pandas==1.1.0
- bs4==0.0.1
- beautifulsoup4==4.9.1
- openpyxl==3.0.4
