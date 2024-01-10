import os
import mysql.connector
import xml.etree.ElementTree as ET

# Create the 'client_data' database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="b26354"
)
mycursor = mydb.cursor()
mycursor.execute("SHOW DATABASES")
databases = mycursor.fetchall()
database_exists = False
for database in databases:
        if 'client_data' in database:
                database_exists = True
                break

if not database_exists:
        mycursor.execute("CREATE DATABASE client_data")

# Get the list of XML files in the data/ folder
xml_files = os.listdir("data/")
for i, file in enumerate(xml_files):
        print(f"{i+1}. {file}")

# Ask the user to select a file
selected_file = int(input("Select the number associated with the file you want to use: "))
xml_file = xml_files[selected_file - 1]

# Ask the user for the client name
client_name = input("Enter the client name: ")

# Create the table in the 'client_data' database
mycursor.execute(f"USE client_data")

# Check if the table exists
mycursor.execute(f"SHOW TABLES LIKE '{client_name}'")
table_exists = mycursor.fetchone()

# Drop the table if it exists
if table_exists:
        mycursor.execute(f"DROP TABLE {client_name}")

mycursor.execute(f"CREATE TABLE {client_name} (Domain VARCHAR(56), BUID VARCHAR(64), Type VARCHAR(32), Level VARCHAR(32), Baseline_Related_CSF_Entry VARCHAR(128), Baseline_Requirement_Statement TEXT, Elements TINYINT, IP_Policy TEXT, IP_Procedure TEXT, IP_Implemented TEXT)")


# Read the selected XML file
tree = ET.parse(f"data/{xml_file}")
print(f'XML File is: {xml_file}')
root = tree.getroot()

# i = 1

# Iterate through the XML file and insert the attribute data into the database table
for domain_name in root.findall(".//{IllustrativeProceduresReport}Domain_Name[@Textbox31]"):
    # Navigate to Baseline_Requirement_Statement_Collection
    brs_collection = domain_name.find("{IllustrativeProceduresReport}Baseline_Requirement_Statement_Collection")
    
    # Iterate through each Baseline_Requirement_Statement
    for brs in brs_collection.findall("{IllustrativeProceduresReport}Baseline_Requirement_Statement"):
        buid = brs.get("Baseline_Unique_ID")
        type = brs.get("Type")
        level = brs.get("Level")
        baseline_related_csf_entry = brs.get("Baseline_Related_CSF_Entry")
        baseline_requirement_statement = brs.get("Baseline_Requirement_Statement")
        elements = brs.get("Elements")
        
        # Iterate through each Details element within the Details_Collection
        details_collection = brs.find("{IllustrativeProceduresReport}Details_Collection")
        if details_collection is not None:
            for detail in details_collection.findall("{IllustrativeProceduresReport}Details"):
                ip_policy = detail.get("IP___Policy2")
                ip_procedure = detail.get("IP___Procedure2")
                ip_implemented = detail.get("IP___Implementation2")

                if ip_policy and ip_procedure and ip_implemented:
                    # Process the data or insert into database
                    pass
        else:
            ip_policy = ip_procedure = ip_implemented = None

        #print(f'Count = {i} / BUID = {buid} / ip_policy = {ip_policy}')
        #i += 1

        #break

        # Insert the data into the database table
        sql = f"INSERT INTO {client_name} (Domain, BUID, Type, Level, Baseline_Related_CSF_Entry, Baseline_Requirement_Statement, Elements, IP_Policy, IP_Procedure, IP_Implemented) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (domain_name.get("Textbox31"), buid, type, level, baseline_related_csf_entry, baseline_requirement_statement, elements, ip_policy, ip_procedure, ip_implemented)
        mycursor.execute(sql, val)

# Commit the changes and close the database connection
mydb.commit()
mydb.close()
