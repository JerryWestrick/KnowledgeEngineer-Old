 ## AWS / EC2 parameters
 - asterisk is installed on AWS ec2.
 - using nat so make all configurations accordingly
 - private subnet: 172.31.0.0/20
 - private address: 172.31.12.144
 - public address: 18.191.115.60

 ## realtime
 - Use realtime using postgresql 

 ## Sip Module
 - It is using pjsip module
 - Sip Port was moved to 55060

## IAX Module
 - IAX support is required. 
 - move UDP port 9876

 ## Employees / endpoints / extensions:
 - the list of employees is stored in EmployeeTelephoneList.csv

 ## Functionality
 -  support VOIP soft-phones mainly over IAX

 ### Dialling

1. To call an employee a caller would dial the employee's desk extension,
   - which would ring for 30 seconds,
   - if no answer then it would ring on their phone for 30 seconds,
   - If no answer then the caller would be asked to leave a message,
   - which would be sent to employee's email.

2. It is possible to call a persons phone directly
   - which would ring for 30 seconds,
   - If no answer then the caller would be asked to leave a message,
   - which would be sent to employee's email.


 ### Video Conferencing
 - Allow for Audio and Video conferencing
