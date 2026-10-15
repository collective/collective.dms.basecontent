*** Settings ***
Documentation  collective.dms.basecontent keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Fixture (testing.py, DMS_TESTS_PROFILE): user siteadmin in the Administrators group;
...            the categories vocabulary creates the default category when a file form is opened.
Resource  ui_plone${PLONE_MAJOR}.robot
Library  OperatingSystem


*** Variables ***
${SITE_ADMIN}  siteadmin
${SITE_ADMIN_PASSWORD}  SiteAdm!n0


*** Keywords ***
Log in as site admin
    Log in with the login form  ${SITE_ADMIN}  ${SITE_ADMIN_PASSWORD}

A file to upload
    [Documentation]  Path of a new file of the robot output directory
    [Arguments]  ${filename}  ${content}=File content
    Create file  ${OUTPUT DIR}${/}${filename}  ${content}
    [Return]  ${OUTPUT DIR}${/}${filename}

Add a document
    [Documentation]  With the add menu of the site root; leaves the browser on the document view
    [Arguments]  ${title}
    Go to  ${PLONE_URL}
    Click the add menu item  dmsdocument
    Input text  css=#form-widgets-IDublinCore-title  ${title}
    Save the form
    The status message contains  Item created

Add a version
    [Documentation]  Main file (dmsmainfile), with the add menu of the document view
    [Arguments]  ${document_url}  ${title}  ${path}
    Go to  ${document_url}
    Click the add menu item  dmsmainfile
    Input text  css=#form-widgets-title  ${title}
    Choose file  css=#form-widgets-file-input  ${path}
    Save the form
    The status message contains  Item created

Add an appendix
    [Documentation]  Appendix file (dmsappendixfile), with the add menu of the document view
    [Arguments]  ${document_url}  ${title}  ${path}
    Go to  ${document_url}
    Click the add menu item  dmsappendixfile
    Input text  css=#form-widgets-IBasic-title  ${title}
    Choose file  css=#form-widgets-file-input  ${path}
    Save the form
    The status message contains  Item created

The version row
    [Documentation]  Locator of the row of the versions table showing this title
    [Arguments]  ${title}
    [Return]  xpath=//div[@id="fieldset-versions"]//table[contains(@class, "iconified-listing")]//tr[td[contains(@class, "title-column")]//a[normalize-space()="${title}"]]

The appendix row
    [Documentation]  Locator of the row of the appendixes table (below the fields) showing this title
    [Arguments]  ${title}
    [Return]  xpath=//fieldset[legend[normalize-space()="Appendix"]]//table[contains(@class, "iconified-listing")]//tr[td[contains(@class, "title-column")]//a[normalize-space()="${title}"]]

The row links to the file
    [Documentation]  Title link to the file and download action of a versions/appendixes table row
    [Arguments]  ${row}  ${file_url}
    Page should contain element  ${row}//td[contains(@class, "title-column")]//a[@href="${file_url}"]
    Page should contain element  ${row}//td[contains(@class, "action-column")]//a[contains(@href, "/@@download")]

The field shows
    [Documentation]  Field of a display form (document view)
    [Arguments]  ${field_name}  ${text}
    Element should contain  css=#form-widgets-${field_name}  ${text}
