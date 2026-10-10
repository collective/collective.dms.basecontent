*** Settings ***
Documentation  The dms document: added with the add menu, edited, its view shows the fields next to the versions.
Resource  dms_basecontent.robot
Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***
Add a document with the add menu
    Log in as site admin
    Add a document  Contract
    Location should be  ${PLONE_URL}/contract/view
    Element should contain  css=#content h1  Contract
    Element should contain  css=#fieldset-versions legend  Versions
    Element should contain  css=#fieldset-versions  There is no version note for this document.
    Page should contain element  css=#formfield-form-widgets-notes
    Page should contain element  css=#formfield-form-widgets-treating_groups
    Page should contain element  css=#formfield-form-widgets-recipient_groups
    Page should contain element  css=#formfield-form-widgets-related_docs
    The page is not an error

Edit the document and see the saved values
    Log in as site admin
    Add a document  Contract
    Click the content view  edit
    Input text  css=#form-widgets-notes  Signed by both parties
    Select in the multiple selection widget  treating_groups  Reviewers
    Select in the multi select2 widget  recipient_groups  Site Administrators
    Save the form
    The status message contains  Changes saved
    The field shows  notes  Signed by both parties
    The field shows  treating_groups  Reviewers
    The field shows  recipient_groups  Site Administrators
    Element should not contain  css=#form-widgets-recipient_groups  Reviewers

The dms document edit form shows the versions next to the fields
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Go to  ${PLONE_URL}/contract/@@dmsdocument-edit
    Element should contain  css=h1.documentFirstHeading  Edit DmsDocument
    Page should contain element  css=form#form #fieldset-versions
    ${row} =  The version row  Version 1
    Page should contain element  ${row}
    Input text  css=#form-widgets-notes  Second version expected
    Save the form
    The status message contains  Changes saved
    Location should be  ${PLONE_URL}/contract
    The field shows  notes  Second version expected

The related documents link to each other
    [Documentation]  The view of A lists B (related document), the view of B lists A (back reference)
    Enable autologin as  Manager
    ${uid_a} =  Create content  type=dmsdocument  id=doc-a  title=Document A
    ${uid_b} =  Create content  type=dmsdocument  id=doc-b  title=Document B
    Set field value  ${uid_a}  related_docs  ["${uid_b}"]  references
    Log in as site admin
    Go to  ${PLONE_URL}/doc-a
    The patterns are initialized
    Element should be visible  xpath=//*[@id="form-widgets-related_docs"]//a[@href="${PLONE_URL}/doc-b"][normalize-space()="Document B"]
    Go to  ${PLONE_URL}/doc-b
    The patterns are initialized
    Element should be visible  xpath=//*[@id="form-widgets-related_docs"]//a[@href="${PLONE_URL}/doc-a"][normalize-space()="Document A"]
