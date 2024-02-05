# Loan application Fraud detection
Graph for loan application fraud detection involves representing various entities involved in the loan 
application process and the relationships between them. This graph can be instrumental in identifying 
patterns and connections that might indicate fraudulent activity.


## Entities (Vertices)
- Applicants: Representing individuals applying for loans.
- Applications: Specific loan applications.
- Banks: Financial institutions where applications are submitted.
- Addresses: Physical addresses provided by applicants.
- Employers: Employment details provided by applicants.
- Phone Numbers: Contact details provided by applicants.
- Bank Accounts: Linked bank accounts for transactions.

## Relationships (Edges)
- Submitted Application: Linking applicants to their applications.
- Applied To: Applications are applied to specific banks.
- Resides At: Linking applicants to addresses.
- Employed By: Connecting applicants to their employers.
- Contact Number: Associating phone numbers with applicants.
- Uses Account: Linking bank accounts to applicants.

## Create graph
```gremlin
// Add Applicant vertices
g.addV('applicant').property('name', 'Applicant1').as('applicant1')
// ... more applicants

// Add Application vertices
g.addV('application').property('id', 'Application1').as('application1')
// ... more applications

// Add Bank vertices
g.addV('bank').property('name', 'BankA').as('bankA')
// ... more banks

// Add Address vertices
g.addV('address').property('location', 'Address1').as('address1')
// ... more addresses

// Add Employer vertices
g.addV('employer').property('name', 'Employer1').as('employer1')
// ... more employers

// Add Phone Number vertices
g.addV('phone_number').property('number', 'PhoneNumber1').as('phoneNumber1')
// ... more phone numbers

// Add Bank Account vertices
g.addV('bank_account').property('account_number', 'Account1').as('account1')
// ... more bank accounts

// Add edges
g.addE('submitted_application').from('applicant1').to('application1')
g.addE('applied_to').from('application1').to('bankA')
g.addE('resides_at').from('applicant1').to('address1')
g.addE('employed_by').from('applicant1').to('employer1')
g.addE('contact_number').from('applicant1').to('phoneNumber1')
g.addE('uses_account').from('applicant1').to('account1')
// ... more edges for other entities

```

## Queries
- retrieves all loan applications submitted by 'Applicant1'.
```gremlin
g.V().has('applicant', 'name', 'Applicant1').out('submitted_application').values('id')

```

- Lists applicants who have applied for loans at more than one bank, which could be a potential
fraud indicator.
```gremlin
g.V().hasLabel('applicant').as('applicant').out('submitted_application').out('applied_to').dedup().groupCount().by(select('applicant')).unfold().where(values.is(gte(2)))

```

- Detects addresses that are linked to multiple applicants, a possible sign of fraudulent activity.
```gremlin
g.V().hasLabel('address').group().by('location').by(in('resides_at').dedup().count()).unfold().where(values.is(gte(2)))

```
-  find clusters of applicants from the same employer, which might be normal or could indicate a coordinated fraud attempt.

```gremlin
g.V().has('employer', 'name', 'Employer1').in('employed_by').values('name')
```

- query finds instances where different applicants have provided the same contact details.
```textmate
g.V().hasLabel('phone_number').as('phone').in('contact_number').dedup().count().where(is(gte(2))).select('phone').values('number')
```

- Applicants applying at multiple banks 
```textmate
g.V().hasLabel('applicant').as('a').out('submitted_application').out('applied_to').dedup().count().where(is(gte(2))).select('a').values('name')

```

- Frequent changes in addresses might be a red flag for potential fraud.
```textmate
g.V().hasLabel('applicant').as('applicant').out('resides_at').groupCount().by('location').unfold().where(values.is(gte(2))).select(keys).as('address').select('applicant', 'address')

```