import sys

with open('backend/main.py', 'r') as f:
    content = f.read()

# Check for the SQLAlchemy relation error on Memecoin that was in the logs
# The logs also showed:
# ERROR    main:main.py:1558 Failed to publish strategy: Could not determine join condition between parent/child tables on relationship Memecoin.positions - there are no foreign keys linking these tables.  Ensure that referencing columns are associated with a ForeignKey or ForeignKeyConstraint, or specify a 'primaryjoin' expression.
# This means there's a missing foreign key or primaryjoin on the Memecoin.positions relationship.
