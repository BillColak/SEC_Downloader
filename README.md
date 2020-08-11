# SEC_Downloader
This code allows you to download SEC financial statements as pandas dataframes and converts it into Excel.
If you have any suggestions on how to improve this project or would like to contribute please let me know.

Why use this code
------------
- XBRL with your own validation, it will allow for multiple company comparison over periods of time.
- Download Financial Statements in mass. Hence why the XBRL taxonomy is included.
- Other online options fail as this code is more rigorously tested.
- instead of directly downloading the excel files, it scrapes html versions with xbrl taxonomy which allows enables
 integration into other code projects.
 - https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/about-readmes

Screenshots
-----------

<https://i.imgur.com/r7rbBOT.png>

<https://i.imgur.com/piorgI8.png>

Requirements
------------
- requests==2.24.0
- pandas==1.1.0
- bs4==0.0.1
- beautifulsoup4==4.9.1
- openpyxl==3.0.4