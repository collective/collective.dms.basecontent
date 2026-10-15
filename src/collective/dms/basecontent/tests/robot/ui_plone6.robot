*** Settings ***
Documentation  Plone 6 Classic UI keywords. Same keyword names and arguments as ui_plone4.robot.
...            Robot Framework 3.0 syntax: shared with the Plone 4.3 (Python 2) environment.
...            Selectors checked on Plone 6.1 (collective.contact.contactlist) and 6.2 (collective.dms.basecontent).
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote

*** Variables ***
${MODAL}  css=.modal-dialog
${ERROR_PAGE_TEXT}  there seems to be an error
${NOT_FOUND_TEXT}  This page does not seem to exist

*** Keywords ***
Log in with the login form
    [Documentation]  Real login (creates the user folder), unlike autologin
    [Arguments]  ${username}  ${password}
    Disable autologin
    Go to  ${PLONE_URL}/login
    Input text  css=#__ac_name  ${username}
    Input password  css=#__ac_password  ${password}
    # the login button stays disabled until the pattern of the form is initialized
    Wait until page does not contain element  css=#buttons-login.disabled
    Click button  css=#buttons-login
    Wait until page contains element  css=#personaltools-menulink

Click the content action
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions-${action_id}
    Click element  css=#plone-contentmenu-actions-${action_id}

The content action is available
    [Arguments]  ${action_id}  ${expected}=${True}
    Click element  css=#plone-contentmenu-actions > a
    Wait until element is visible  css=#plone-contentmenu-actions ul
    Run keyword if  ${expected}
    ...  Page should contain element  css=#plone-contentmenu-actions-${action_id}
    ...  ELSE  Page should not contain element  css=#plone-contentmenu-actions-${action_id}

Open the add menu
    Click element  css=#plone-contentmenu-factories > a
    Wait until element is visible  css=#plone-contentmenu-factories ul

The personal action links to
    [Documentation]  Item of the user menu (user actions), by action id
    [Arguments]  ${action_id}  ${url}
    Element attribute value should be  css=#personaltools-${action_id}  href  ${url}

The personal action is not available
    [Arguments]  ${action_id}
    Page should not contain element  css=#personaltools-${action_id}

The modal is open
    [Documentation]  Overlay (Plone 4) or modal (Plone 6) showing a form
    Wait until element is visible  ${MODAL} form

Modal element
    [Documentation]  Locator of the element with this id inside the modal
    ...              (an argument starting with # would be a robot comment)
    [Arguments]  ${id}
    [Return]  ${MODAL} [id="${id}"]

Save the modal
    Click button  css=.modal-footer #form-buttons-save

Cancel the modal
    Click button  css=.modal-footer #form-buttons-cancel

The modal is closed
    Wait until page does not contain element  ${MODAL}

The status message contains
    [Arguments]  ${text}
    Wait until element contains  css=.portalMessage  ${text}

The page is not an error
    Page should not contain  ${ERROR_PAGE_TEXT}

The page is not found
    Page should contain  ${NOT_FOUND_TEXT}

The edit link is not available
    Page should not contain element  css=#contentview-edit

Click the content view
    [Documentation]  Tab of the content views (object actions), by action id
    [Arguments]  ${action_id}
    Click link  css=#contentview-${action_id} a

The content action links to
    [Documentation]  Item of the Actions menu (object_buttons), by action id
    [Arguments]  ${action_id}  ${url}
    # Plone 6 adds the CSRF token to the action URLs
    ${href} =  Get element attribute  css=#plone-contentmenu-actions-${action_id}  href
    Should be equal  ${href.split('?_authenticator=')[0]}  ${url}

Click the add menu item
    [Documentation]  Item of the add menu, by portal type
    [Arguments]  ${portal_type}
    Open the add menu
    Click link  css=#plone-contentmenu-factories a#${portal_type}

Select in the multiple selection widget
    [Documentation]  Default widget of a multiple choice field: the ordered selection (from/to lists), as on Plone 4
    [Arguments]  ${field_name}  ${label}
    # not under the sticky form buttons
    Execute javascript  document.getElementById("formfield-form-widgets-${field_name}").scrollIntoView({block: "center", behavior: "instant"})
    Select from list by label  css=#form-widgets-${field_name}-from  ${label}
    Click button  css=#formfield-form-widgets-${field_name} button[name="from2toButton"]

Select in the multi select2 widget
    [Documentation]  Add a value to the multi select2 widget of this field (plone.app.z3cform Select2Widget on Plone 6)
    [Arguments]  ${field_name}  ${label}
    Click element  css=#formfield-form-widgets-${field_name} .select2-choices
    Wait until element is visible  css=#select2-drop .select2-results
    Click element  xpath=//div[@id="select2-drop"]//div[contains(@class, "select2-result-label")][contains(., "${label}")]
    Wait until element is not visible  css=#select2-drop

Select the display view
    [Documentation]  Item of the Display menu, by view id (not checked on Plone 6: only used by test_documentviewer.robot)
    [Arguments]  ${view_id}
    Click element  css=#plone-contentmenu-display > a
    Wait until element is visible  css=#plone-contentmenu-display-${view_id}
    Click element  css=#plone-contentmenu-display-${view_id}

Save the form
    [Documentation]  Save button of a z3c.form page (add or edit form)
    # not under the sticky form buttons, and enabled (the button is disabled until the patterns are loaded)
    Execute javascript  document.getElementById("form-buttons-save").scrollIntoView({block: "center", behavior: "instant"})
    Wait until page does not contain element  css=#form-buttons-save.disabled
    Click button  css=#form-buttons-save

The patterns are initialized
    [Documentation]  Mockup initializes some patterns asynchronously, after the page load (body.patterns-loaded):
    ...              a wrong pattern hid the related documents links 0.25 s later
    Wait until page contains element  css=body.patterns-loaded
    Sleep  2s
