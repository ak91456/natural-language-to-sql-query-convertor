import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "NumbersStation/nsql-350M"


class SQLModel:
    """
    Thin wrapper around nsql-350M.

    Alternatives (swap MODEL_NAME above):
      - "NumbersStation/nsql-6B"         — much more accurate, needs ~12 GB VRAM
      - "NumbersStation/nsql-llama-2-7B" — Llama-2 based, needs ~14 GB VRAM
      - "defog/sqlcoder-7b-2"            — state-of-the-art open source
    For best accuracy with no local GPU, use the Claude or OpenAI API instead.
    """

    _instance = None

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        self.model.eval()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_schema_sql(self, schema):
        parts = []
        for table, columns in schema.items():
            col_defs = ",\n    ".join(f"{col} {dtype}" for col, dtype in columns)
            parts.append(f"CREATE TABLE {table} (\n    {col_defs}\n)")
        return "\n\n".join(parts)

    def generate_sql(self, natural_language_query, schema):
        """
        Generate a SQL SELECT query from a natural language question.

        schema: {table_name: [(col_name, data_type), ...]}
        Returns the generated SQL string.
        """
        schema_sql = self._build_schema_sql(schema)
        # nsql models expect the prompt to end with SELECT so they complete it.
        prompt = (
            f"{schema_sql}\n\n"
            f"-- Using valid PostgreSQL, answer the following question "
            f"for the tables provided above.\n\n"
            f"-- {natural_language_query}\n"
            f"SELECT"
        )

        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=256,
                num_beams=4,
                early_stopping=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode only the newly generated tokens (everything after the prompt).
        new_tokens = generated_ids[0][input_ids.shape[1]:]
        completion = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return ("SELECT" + completion).strip()
