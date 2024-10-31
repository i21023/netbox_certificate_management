# NetBox Certificate Management Plugin
A small NetBox plugin which allows users to store x.509 v3 certificates in NetBox

## Supported Certificate Fields

The following fields get parsed and displayed by the plugin
- Subject
- Issuer
- Serial Number
- Not valid after
- Not valid before
- Subject Public Key
- Subject Public Key Algorithm
- Extension Fields:
    - Subject Alternative Names 
    - Basic Constraints
    - Key Usage
    - Extended Key Usage
    - CRL Distribution Points

# Features

The following features are available:
- Upload a certificate file in a supported format[^1] to parse the fields
- Download a uploaded certificate in PEM or binary format
- Reference a parent certificate to show display certificate chains
- See if a certificate is about to expire
- REST and GraphQL API support


[^1]: supported formats are: PEM, Binary, PKCS#12 

