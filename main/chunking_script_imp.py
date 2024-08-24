
import spacy
# !python -m spacy download en_core_web_lg --quiet
nlp = spacy.load("en_core_web_lg")
from transformers import AutoTokenizer

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("model_name_or_path")


## Load the tokenizer and model from Groq API


def count_tkn_with_tokenizer(txt:str):
    return len(tokenizer(txt)['input_ids'])

def create_chunks (sentences, doc_chunk_len: int = 484):
    max_chunk_token_len = doc_chunk_len

    chunks = []
    current_chunk_tkn_len = 0
    current_chunk = ""

    for sentence in sentences:
        word_tkn_len = count_tkn_with_tokenizer(sentence)

        if current_chunk_tkn_len + word_tkn_len < max_chunk_token_len:
            current_chunk += str(sentence + " ")
            current_chunk_tkn_len += word_tkn_len
        else:
            chunks.append(current_chunk.strip())
            current_chunk = str(sentence + " ")
            current_chunk_tkn_len = word_tkn_len

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

## Load full_text i.e. the text to be summarized

nlp.max_length = len(full_text) + 10000
sentences = [sent.text for sent in nlp(full_text).sents]

doc_chunk_len = 484
chunks = create_chunks(sentences, doc_chunk_len)