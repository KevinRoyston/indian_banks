import pandas as pd
from flask import Flask, request, jsonify
from ariadne import QueryType, make_executable_schema, gql, graphql_sync
from flask_cors import CORS
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data():
    try:
        
        df_branches = pd.read_csv('bank_branches.csv')  
        df_branches['branch'] = df_branches['branch'].fillna('Unknown')
        df_branches['bank_name'] = df_branches['bank_name'].fillna('Unknown')
        df_branches['ifsc'] = df_branches['ifsc'].fillna('Unknown')
        return df_branches.to_dict(orient='records')
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return []


BANKS = load_data()


type_defs = gql("""
    type Bank {
        name: String!
    }

    type Branch {
        branch: String!
        bank: Bank
        ifsc: String!
    }

    type Query {
        branches: [Branch!]!
    }
""")

query = QueryType()

@query.field("branches")
def resolve_branches(_, info):
    try:
       
        return [
            {
                "branch": branch["branch"],
                "bank": {"name": branch.get("bank_name", "Unknown")},
                "ifsc": branch["ifsc"]
            }
            for branch in BANKS
        ]
    except Exception as e:
        logging.error(f"Error resolving branches: {e}")
        return []

schema = make_executable_schema(type_defs, query)

app = Flask(__name__)
CORS(app)  

@app.route('/gql', methods=['POST'])
def handle_graphql_request():
    try:
        data = request.get_json()
        success, result = graphql_sync(
            schema,
            data,
            context_value=None,
            middleware=[]
        )
        status_code = 200 if success else 400
        return jsonify(result), status_code
    except Exception as e:
        logging.error(f"Error handling GraphQL request: {e}")
        return jsonify({'errors': [{'message': 'Internal server error'}]}), 500

@app.route('/')
def graphql_playground():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>GraphQL Playground</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.24/build/static/css/index.css" />
        <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react@1.7.24/build/static/js/middleware.js"></script>
    </head>
    <body>
        <div id="root"></div>
        <script>
            window.addEventListener('load', function (event) {
                GraphQLPlayground.init(document.getElementById('root'), {
                    endpoint: '/gql'
                });
            });
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
