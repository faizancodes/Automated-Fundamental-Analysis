# Automated Fundamental Analysis via Python

This python program rates stocks out of 100 based on valuation, profitability, growth, and price performance metrics, relative to sector.


View the file `StockRatings-04.05.22.csv` as an example of the output of this program

# How to Run the Code

  1. Clone the repository `git clone https://github.com/faizancodes/Automated-Fundamental-Analysis.git`
  2. Run `cd Automated-Fundamental-Analysis`
  3. Download all the dependencies `pip install -r requirements.txt` 
  4. Run `stockgrader.py`, this will scrape data from all 8300+ stocks on Finviz.com and grade each of them out of 100
     - The program will also generate the CSV files you can use for analysis
  5. Open the csv file created from the program through Excel and analyze!

# How to Run the Web App
  1. Run `cd WebApp`
  2. Run `streamlit run app.py`
     - If that does not work, run `py -m streamlit run app.py`
  3. Open the web app in your browser, it will be on localhost

# Web App Screenshots

<img src="https://user-images.githubusercontent.com/43652410/161826590-455f2d30-5605-42c5-a8c1-2c1c75d03d26.png" width="750" height="900">
<img src="https://user-images.githubusercontent.com/43652410/161826910-83856a1c-e7d2-454c-b0df-1bb06251d3f7.png" width="750" height="900">


# Grading System

The grading system used in this program is based on the normal distribution of values for a certain metric for a specified sector. For example, if I want to grade the Net Margin of a stock in the Technology sector, I look at the net margins of all the stocks in the technology sector and grade the stock's net margin based on its percentile in the distribution of values.

In the figure below, we see that the average net margin for a stock in technology sector is 1.8% and the 90th percentile is 16.45%. The grading system utilized in the program takes the standard deviation of the set of values after removing outliers and divides that number by 3, which is represented by the 'Change' value shown in the figure, equaling 4.68. This is the value that is used to grade each metric for each stock. 


<img src="https://user-images.githubusercontent.com/43652410/98454501-06703e00-2133-11eb-8521-c5c532a759c1.png" width="500" height="400" alt="">


The figure shown below represents exactly how each metric is graded, where each bar in the graph is representative of 1 increment of the 'Change' value. 
Based on this figure and the 'Change' value, a stock in the technology sector with a net margin of:
  - 17% is rated A+
  - 15% is rated A
  - 11% is rated A- 
  
<img src="https://user-images.githubusercontent.com/43652410/98454570-f442cf80-2133-11eb-8a3a-cee8da8a3f59.jpg" width="650" height="500" alt="">


After all the metrics in each category of valuation, profitability, growth, and price performance are graded, the grades are then converted to numbers and then the average of the values is computed. To get the overall rating of a stock, these numerical ratings for each category are added together and multiplied to get a score out of 100. 

For metrics where a lower value is considered better, such as P/E ratios, the algorithm will use the 10th percentile as the basis for grading. So if a stock in the Technology sector has a P/E ratio of 10 and that is in the 10th percentile of all P/E ratios for Technology stocks, it will be rated A+. 