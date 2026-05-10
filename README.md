# Database_performance_AI
Performance sugestions using AI. 

Modelo: Qwen 2.5 Coder 7B GGUF. 
Hardware: GPU 8GBVRAM. 
Local RAG: Everything is in local. 

Work-flow: 
- User upload a .sql
- System extract tables and relations using sqlglot
- User ask for example: "What happen if I incress the size of the COD_POSTAL camp?"
- Think (qwen): The model search into metadata and respond. 

Ollama serve: init a server. 
ollama pull [model]: Download the model. 
ollama rm [model]: Delete model from disk. 
ollama list: Show all models you have. 


# Vista general del proyecto:

- Frontal hecho en streamlit donde se interactúa con el proyecto.

- Distintos .pdm en una carpeta que se transforman a .json usando python. Desde el frontal cada vez que insertas un .pdm se genera un .json del modelo.

- En otro apartado del frontal insertas una query y el modelo qwen2.5-coder:7b teniendo en cuenta el JSON que tiene las tablas que hace referencia la query, te recomendará cambiar la query y/o modificar la base de datos.

## Flujo actual:  
DPM -> JSON -> Streamlit -> LLM

### Recomendacions: 
- Base de datos. 
    - En lugar de tener archivos JSON sueltos, es mejor guardarlos en una bae de datos vectorial o en un esquema SQL ligero (SQLite) para que el sistema solo busca las tablas relevantes (tecnica RAG) y pasarselo a la LLM en véz de pasarle todo el modelo de datos. 

- Validación de la query que se pasa. 
    - sqlglot o sqlfluff para analizar si la query es válida. 
    - LLM analiza la lógica. ej: "Estas haciendo JOIN con una tabla que no existe en el PDM", "Falta un filtro de fecha que es obligatorio en el modelo". 

- Sugerencias técnicas específicas. 
    - Feedback Loop: botón para aplicar cambios el se ejecuta en una base de datos de prueba para confirmar que funciona. 

- Visualización. 
    - graphviz para mostar un diagrama de tablas que la query está tocando. 
