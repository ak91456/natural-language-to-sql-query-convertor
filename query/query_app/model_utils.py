# query_app/model_utils.py
from transformers import AutoTokenizer, AutoModelForCausalLM

class SQLModel:
    def __init__(self):
        # Load the tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained("NumbersStation/nsql-350M")
        self.model = AutoModelForCausalLM.from_pretrained("NumbersStation/nsql-350M")

    def generate_sql(self, natural_language_query, db_name, table_name):
        # Construct the input text for the model
        text = f"""
        CREATE TABLE stadium (
            stadium_id number,
            location text,
            name text,
            capacity number,
            highest number,
            lowest number,
            average number
        )

        CREATE TABLE singer (
            singer_id number,
            name text,
            country text,
            song_name text,
            song_release_year text,
            age number,
            is_male others
        )

        CREATE TABLE concert (
            concert_id number,
            concert_name text,
            theme text,
            stadium_id text,
            year text
        )

        CREATE TABLE singer_in_concert (
            concert_id number,
            singer_id text
        )

        -- Using valid SQLite, answer the following questions for the tables provided above.

        -- {natural_language_query}
        """

        input_ids = self.tokenizer(text, return_tensors="pt").input_ids

        # Generate SQL query
        generated_ids = self.model.generate(input_ids, max_length=500)
        sql_query = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        return sql_query
