from groq import Groq
import pandas as pd
import sqlite3

def showTable(database):
    table_name = str(database).split(".")[0]
    table_name_1 = str("\'")+str("Image_Record_SQLDB_TABLE")+str("\'")
    sql_query_1 = str("select * from (")+str(table_name_1)+str(") limit 10")
    
    connection_1 = sqlite3.connect(database)
    cursor_1 = connection_1.cursor()
    cursor_1.execute(sql_query_1)

    # cursor.execute(query_1)
    schema = cursor_1.fetchall()
    schema = [_ for _ in schema]
    
    column_name = tablecolumnName(database)
    # st.write(column_name)
    schema = pd.DataFrame(schema, columns = column_name)
    
    return schema

def tablecolumnName(database):
    
    table_name = str(database).split(".")[0]
    table_name_1 = str("\'")+str("Image_Record_SQLDB_TABLE")+str("\'")
    sql_query_1 = str("pragma table_info(")+str(table_name_1)+str(")")
    
    connection_1 = sqlite3.connect(database)
    cursor_1 = connection_1.cursor()
    cursor_1.execute(sql_query_1)

    # cursor.execute(query_1)
    schema = cursor_1.fetchall()
    
    column_name = []
    
    for column in schema:
        # print(column[1], column[2])
        column_name.append(column[1])
    # st.write(column_name)
    return column_name
    
    
def tableDetails(database):
    
    table_name = str("Image_Record_SQLDB_TABLE")
    table_name_1 = str("\'")+str("Image_Record_SQLDB_TABLE")+str("\'")
    sql_query_1 = str("pragma table_info(")+str(table_name_1)+str(")")
    
    connection_1 = sqlite3.connect(database)
    cursor_1 = connection_1.cursor()
    cursor_1.execute(sql_query_1)

    # cursor.execute(query_1)
    schema = cursor_1.fetchall()
    
    column_name = []
    data_type = []
    
    for column in schema:
        # print(column[1], column[2])
        column_name.append(column[1])
        data_type.append(column[2])
      
    table_info = {}
    table_info['Column Name'] = column_name
    table_info[' Corresponding Datatype of Column'] = data_type

    return [table_name, table_info]


def read_sql_databse(database, sql_query):
    
    connection_1 = sqlite3.connect(database)
    cursor_1 = connection_1.cursor()
    cursor_1.execute(sql_query)
    datas = cursor_1.fetchall()
    connection_1.commit()
    connection_1.close()
    
    return datas

 
def generateQuery(database_name, enter_query):
    
    
    ##############################
    
    # Groq model set up with llama2-70b model
    Gorq_Key = str("Enter your Groq API Key")
    groq_model = Groq(api_key = str(Gorq_Key))

    ##############################

    sql_table = database_name
    table_details = tableDetails(sql_table)
    table_name, table_info = table_details[0], table_details[1]


    ###############################

    try:
        prompt_1 = f"""You are an expert in converting English question to SQL query.
                    Here the SQL database details where SQL database name: {table_name} and SQL database details: {table_info}.
                    \nFor example, One SQL database example has given below.
                    \nThe SQL database has the name STUDENT and has the following columns - NAME, CLASS,
                    SECTION & MARKS \n\nFor example,\n

                    
                    \nExample 1: how much marks ram got ?, 
                    the SQL command will be somthing like this SELECT MARKS FROM STUDENT WHERE NAME = "Ram" ;
                    \nExample 2: Give me the full details of table/database, or summarize the database/table/data, or give me brief summary about dataset,
                    the SQL command will be somthing like this SELECT * FROM STUDENT LIMIT 10;
                    \nExample 3: How many entries of records are present?,
                    the SQL command will be somthing like this SELECT COUNT(*) FROM STUDENT;
                    \nExample 4: Tell me all the students studying in Data science class?,
                    the SQL command will be something like this SELECT * FROM STUDENT where CLASS = "Data science";
                    \nExample 5: Give me average number and also provide me the name of highest marks getter for class wise from student table,
                    the SQL command will be something like this SELECT CLASS, AVG(MARKS) AS AVERAGE_MARKS, MAX(MARKS) AS HIGHEST_MARKS FROM STUDENT UNION SELECT NAME, CLASS, MAX(MARKS) AS HIGHEST_MARKS FROM STUDENT GROUP BY CLASS;
                    \nExample 6: Share table details,
                    the SQL command will be something like this pragma table_info(STUDENT)
                    
                    Always only return SQL query. Do not return anything except SQL Query.
                    
                    also the SQL code should not have ``` in begnning or end and SQL word in output.
                    """
                    
        sub_prompt_1 = f"""If the user ask multiple question in a single query then first generate SQL query for individual \
                        question and then concatenate the multiple SQL query for individual question into a single sql query \
                        and share the single merged single sql query. \n\nFor example, \n
                        \nExample 1: Give me average number and also provide me the name of highest marks getter for class wise from student table.
                        Processing Part: \n
                        \nstep 1:\n
                        First divide `Example 1` into individual query, for this example, first query will be `Give me average number from student table`, \
                        the SQL command will be something like this SELECT AVG(MARKS) AS AVERAGE_MARKS FROM STUDENT; \
                        and second query is `provide me the name of highest marks getter for class wise from student table`, and \
                        the SQL command will be something like this SELECT NAME, CLASS, MAX(MARKS) AS HIGHEST_MARKS FROM STUDENT GROUP BY CLASS;
                        \nstep 2:\n
                        Then concatenate the all individual SQL qurey using `UNION` clause. For this example, the combined SQL command will be like \
                        this SELECT CLASS, AVG(MARKS) AS AVERAGE_MARKS, MAX(MARKS) AS HIGHEST_MARKS FROM STUDENT UNION SELECT NAME, CLASS, MAX(MARKS) AS HIGHEST_MARKS FROM STUDENT GROUP BY CLASS;
                        """
       
        
        response_1 = groq_model.chat.completions.create(
            model = "llama3-70b-8192", 
            messages=[
                {
                    "role": "system",
                    "content": str(prompt_1)+str("\n\n\n")+str(sub_prompt_1) # +str("\n\n\n")+str(sub_prompt_2)
                },
                {
                    "role": "user",
                    "content": str(enter_query)
                }
            ],
            temperature = 0.3,
            max_tokens = 1024,
            top_p = 1,
            stream = False,
            stop = None # ", 6"
        )
       
        result_1 = read_sql_databse(database = database_name, sql_query = str(response_1.choices[0].message.content))

        prompt_2 = f"""You task is to convert the Given List of Details into Simple English Language according to user's asked question.
                    Share your response after conversion from List of Details to Simple English Language.
                    Given List of Details: {[_ for _ in result_1]}
                    User's Asked Question: {enter_query}
                    """


        response_2 = groq_model.chat.completions.create(
                        model = "llama3-70b-8192", 
                        messages=[
                            {
                                "role": "system",
                                "content": str(prompt_2)
                            },
                            {
                                "role": "user",
                                "content": str(enter_query)
                            }
                        ],
                        temperature = 0.3,
                        max_tokens = 1024,
                        top_p = 1,
                        stream = False,
                        stop = None # ", 6"
                    )

        return response_2.choices[0].message.content
        
    except Exception as e:
        return str("Ask individual question!")
       
