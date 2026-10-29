*** Settings ***
Documentation  collective.documentviewer integration: the document view shows the last version in the viewer,
...            a main file offers the viewer layout. Skipped on Plone 6 (documentviewer replaced).
Resource  dms_basecontent.robot
Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***
The document view shows the last version in the document viewer
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Add a version  ${PLONE_URL}/contract  Version 2  ${path}
    Go to  ${PLONE_URL}/contract
    Wait until element is visible  css=#fieldset-versions #DV-container .DV-docViewer
    # the title bar of the viewer is hidden (show_sidebar off), its text names the loaded version
    ${title} =  Get element attribute  css=#fieldset-versions .DV-title  textContent
    Should be equal  ${title.strip()}  Version 2

The document viewer display of a text main file says it is not supported
    [Documentation]  The dmsmainfile type offers the documentviewer layout; a text file is not converted
    ${path} =  A file to upload  contract.txt  Contract content
    Log in as site admin
    Add a document  Contract
    Add a version  ${PLONE_URL}/contract  Version 1  ${path}
    Select the display view  documentviewer
    # the default view of a file is its download (@@display-file), the layout is the view action
    Page should contain  Contract content
    Go to  ${PLONE_URL}/contract/version-1/view
    The status message contains  View changed
    Page should contain  The file is not a supported document type.
    Element should contain  css=#content-views  Document Viewer Settings
    Element should contain  css=#form-widgets-file  contract.txt
