"""Documentation fragments for the vpc_list module"""

specdoc_examples = ['''
- name: List all of the Child Accounts under the current Account
  linode.cloud.child_account_list: {}''']

result_child_accounts_samples = ['''{
    "active_since": "2018-01-01T00:01:01",
    "address_1": "123 Main Street",
    "address_2": "Suite A",
    "balance": 200,
    "balance_uninvoiced": 145,
    "billing_source": "external",
    "capabilities": [
        "Linodes",
        "NodeBalancers",
        "Block Storage",
        "Object Storage"
    ],
    "city": "Philadelphia",
    "company": "Linode LLC",
    "country": "US",
    "credit_card": {
        "expiry": "11/2022",
        "last_four": 1111
    },
    "email": "john.smith@linode.com",
    "euuid": "E1AF5EEC-526F-487D-B317EBEB34C87D71",
    "first_name": "John",
    "last_name": "Smith",
    "phone": "215-555-1212",
    "state": "PA",
    "tax_id": "ATU99999999",
    "zip": "19102-1234"
}''']
