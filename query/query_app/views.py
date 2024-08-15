# query_app/views.py
from django.shortcuts import render
import psycopg2
from .forms import DatabaseForm
from .model_utils import SQLModel

sql_model = SQLModel()

def query_view(request):
    if request.method == 'POST':
        form = DatabaseForm(request.POST)
        if form.is_valid():
            db_name = form.cleaned_data['db_name']
            db_user = form.cleaned_data['db_user']
            db_password = form.cleaned_data['db_password']
            db_host = form.cleaned_data['db_host']
            db_port = form.cleaned_data['db_port']
            table_name = form.cleaned_data['table_name']
            natural_language_query = form.cleaned_data['natural_language_query']
            
            # Generate SQL query using SQLModel
            sql_query = sql_model.generate_sql(natural_language_query, db_name, table_name)
            
            try:
                # Connect to the PostgreSQL database
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port
                )
                cur = conn.cursor()
                cur.execute(sql_query)
                result = cur.fetchall()
                cur.close()
                conn.close()
            except Exception as e:
                result = str(e)

            return render(request, 'results.html', {'sql_query': sql_query, 'result': result})
    else:
        form = DatabaseForm()

    return render(request, 'query.html', {'form': form})
