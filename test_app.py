import unittest
import requests

class TestGraphQLAPI(unittest.TestCase):
    def test_get_branches(self):
        url = "http://localhost:5000/gql"
        query = """
        query {
            branches {
                branch
                bank {
                    name
                }
                ifsc
            }
        }
        """
        response = requests.post(url, json={'query': query})
        data = response.json()

        # Print the response to see if it's coming back correctly
        print("Response data:", data)

        # Assert that 'branches' exists in the response data
        self.assertIn('branches', data.get('data', {}))

if __name__ == "__main__":
    unittest.main(verbosity=2)
