# Senate Structured Domain Specification


## Abbreviations

DN  - Chamber Direction

PN  - Chamber President

VPN - Chamber Vice-President

CCA - High Chamber Coordinator

DG  - General Direction

CS  - Superior Council


## Members

In the Senate, there exist members. Members have:

 - Name
 - Date of incorporation
 - One or more mobile phones
 - One or more emails
 - Political affiliation
 - Professional occupation
 - Past political charges


## Member State

At each moment, a member has a state in the Senate. This state can be:

 - Collaborator
 - Applicant
 - Effective
 - Administrator
 - Expelled

### Inexistent -> Collaborator

When a Member comes to a Dinner, it is incorporated to the Senate and becomes a Collaborator.

### Collaborator -> Applicant

The Collaborators that are interested to join the Senate go through an Interview

### Applicant -> Effective

If an applicant is considered to be a potential Effective, the DN can propose it as
candidate. This proposal is subject to the approval by the DG.

Once the candidate is approved, a referendum for the transition to Effective is made in the
chamber by its Effective members, which must pass with the conformity of at least 2/3 of the voters.

### Effective -> Administrator

In order to transition from Effective to Administrator, a qualified proposal from the CS is needed.
This is followed by a referendum to all Administrators, which must be approved by the majority of the voters.

### Administrator -> Effective

Every year, in January the Administrators must be updated. The CS makes a list 
with the members that should continue to be Administrators. This list must be approved
by at least half of the past Administrators. The Administrators not included in the list
become Effective.

### Collaborator/Applicant -> Expelled

The Collaborators and Applicants can be Expelled at any moment by their DN or the DG.

### Effective -> Expelled

Effective members can only be expelled by the DG.

### Administrator -> Expelled

Administrators can only be expelled by a qualified majority of the CS, followed by a referendum
to all Administrators in which the votes for the expulsion are more than half the Administrators.


## Chambers

The Chambers are numbered. 

Each Member belongs to a single Chamber. 

Members can be transfered between Chambers. 

[comment]: <> (When someone becomes a Collaborator the transfer is between NULL and a Chamber. When it is Expelled, it is from a Chamber to NULL)

Each Chamber has a DN. 

There are two types of Chambers:

 - Nucleous
 - Professional Nucleous
 - High Chamber


## Chamber Direction (DN)

### Nucleous

#### Constitution:

 - President (PN) - Elected by the DG, no term limitations. Must be an Administrator
 - 3 Vocals - Elected by the members of their respective chamber. Their mandate ends at the 1st half of March and at the 2nd half of September
 - Secretary/Vice-secretary [Optional] - Named by the PN, confirmed by the DG. PN can destitute them at any moment


### Professional Nucleous

#### Constitution:

 - President (PN) - Elected by the DG, no term limitations. Must be an Administrator
 - 3 Vocals - Elected by the members of their respective chamber. Their mandate ends at the 2nd half of September
 - Secretary/Vice-secretary [Optional] - Named by the PN, confirmed by the DG. PN can destitute them at any moment
 - Vice-President (VPN) [Optional] - Named by the DG. It can be combined with other charges


### High Chamber

#### Constitution:

 - Coordinator (CCA) - Elected by the CS. Must be an Administrator
 - 3 Vocals - Elected by the DG
 - Secretary/Vice-secretary [Optional] - Named by the PN, confirmed by the DG. PN can destitute them at any moment


## Dinners

There are 3 types of dinners:

 - Chamber dinners
 - Intercameral dinners (bicamerals are included here)
 - Administrator dinners

Each dinner has:

 - Date
 - Place (Address)
