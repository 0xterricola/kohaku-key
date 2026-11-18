# Experimental Security Boundaries

The current hardware experiments verify cryptographic
operations; they do not establish a production-secure signer.

Known unverified properties:

- Spending-key derivation wholly inside the secure element
- Durable nonce reuse prevention after resets or faults
- Security of host-selected signing challenges
- Protection against malicious hosts and ROS attacks
- Constant-time secret-scalar operations
- Trusted device display and transaction-intent approval
- Complete RAILGUN spend authorization

Public test vectors and synthetic keys must be used during
integration. Private wallet material must never be included
in logs, command-line arguments, or repository artifacts.

Hardware installation requires separate explicit authorization.
