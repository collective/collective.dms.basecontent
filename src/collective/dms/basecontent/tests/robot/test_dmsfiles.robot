*** Settings ***
Documentation  The files of a dms document: main files (versions) in the versions table next to the fields,
...            appendix files in the appendixes table below them, the view of a main file.
Resource  dms_basecontent.robot
Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***
Add a version of the document
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Go to  ${PLONE_URL}/contract
    Element should not contain  css=#fieldset-versions  There is no version note for this document.
    ${row} =  The version row  Version 1
    The row links to the file  ${row}  ${PLONE_URL}/contract/version-1
    Page should contain element  ${row}//img[@title="Default Category"]
    Element should contain  ${row}//td[contains(@class, "author-column")]  siteadmin
    # state column of the versions table: dms files have no workflow
    Page should contain element  ${row}//td[contains(@class, "dms.state")]

The versions table lists the last version first
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Add a version  ${PLONE_URL}/contract  Version 2  ${path}
    Go to  ${PLONE_URL}/contract
    Element should contain  xpath=(//div[@id="fieldset-versions"]//table//tbody/tr)[1]  Version 2
    Element should contain  xpath=(//div[@id="fieldset-versions"]//table//tbody/tr)[2]  Version 1

Add an appendix to the document
    ${path} =  A file to upload  annex.txt  Annex content
    Log in as site admin
    Add a document  Contract
    Add an appendix  ${PLONE_URL}/contract  Signed annex  ${path}
    Go to  ${PLONE_URL}/contract
    # an appendix is not a version
    Element should contain  css=#fieldset-versions  There is no version note for this document.
    ${row} =  The appendix row  Signed annex
    The row links to the file  ${row}  ${PLONE_URL}/contract/signed-annex
    Element should contain  ${row}//td[contains(@class, "author-column")]  siteadmin
    # no state column in the appendixes table
    Page should not contain element  ${row}//td[contains(@class, "dms.state")]

The main file add form proposes the next version number
    [Documentation]  Plone 4 bug: the @default_value adapter of the title is not grokked, the field stays empty
    [Tags]  plone4-bug
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Click the add menu item  dmsmainfile
    Textfield value should be  css=#form-widgets-title  1
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Go to  ${PLONE_URL}/contract
    Click the add menu item  dmsmainfile
    Textfield value should be  css=#form-widgets-title  2

The main file view shows the file and its category
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Location should be  ${PLONE_URL}/contract/version-1/view
    Element should contain  css=#form-widgets-file  contract.txt
    The field shows  IIconifiedCategorization-content_category  Default Category
    The content action links to  download  ${PLONE_URL}/contract/version-1/@@download
    Click the content action  view_element
    # Plone 6 adds the CSRF token to the action URLs
    Location should contain  ${PLONE_URL}/contract/version-1/view
    The page is not an error
