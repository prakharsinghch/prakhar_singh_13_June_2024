# prakhar_singh_13_June_2024

# Database ERD 
![image](https://github.com/user-attachments/assets/ce4964ac-2360-463c-b025-2510bf94611a) 

# Files and Their Working

**1. Result csv -> result.csv**

**2. data_cleaning.py**<br/>
  - reads data from the csv files
  - formats into a dict like structure having store id as the key

**3. dataDump.py**
  - creates schema into database
  - takes data from data_cleaning and pushes into the database

**3. db.py**
- contains db configurations
- containas db operations to create report schema

**4. main.py**
- contains the **/trigger_report** and **/get_report/{id}**

**5. playground.py**
- file for me to run and test workflows

**6. report_generation.py**
- handles logic to find uptime and downtime
- writes back to the report and report_data table

# Logic Explanation
**1. last hour update** 
  - store is polled every hour
  - fetch latest status and the status prior to it
  - if both are active -> store was active in the past hour -> set uptime to 60mins **(or diff b/w polls )** and downtime to 0mins
  - latest active but inactive before -> assume the store was active when it was polled -> downtime : 60 mins uptime 0 mins
  - lastest inactive but was active before -> store got inactive when it was polled -> uptime : 60mins and downtime 0mins

  **2. last day and week update** 
   - we know that store is polled every hour
   - count the time store was active or inactive in the operable window for each day.

# Code Improvements: 
- I believe the logic can be improved further, its very crude at the moment
- as the number of stores would grow it would take more time to make the report, we could use multithreading alternatives for faster report generation.
- better data handling, as we only need data for the last week, we can clean the store_status report and keep only relevant data.

# Video Demonstration
https://drive.google.com/drive/folders/1u_yKlRHmklzlfMH9BhU0XemlK4VQ3gFE?usp=sharing


    
