import openpyxl
from openpyxl.styles import Font
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from .models import Feature, TestScenario, TestCase
from datetime import date


def fetch_features_from_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    features_data = {}

    # Extract HTML
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Analyze Forms
    forms = soup.find_all('form')
    features_data['forms'] = analyze_forms(driver, forms)

    # Analyze Buttons
    buttons = soup.find_all('button')
    features_data['buttons'] = analyze_buttons(driver, buttons)

    # Analyze Links
    links = soup.find_all('a')
    features_data['links'] = analyze_links(driver, links)

    driver.quit()
    return features_data


def analyze_forms(driver, forms):
    form_data = []
    for i, form in enumerate(forms):
        form_id = form.get('id', f'form-{i}')
        form_action = form.get('action', 'N/A')
        inputs = form.find_all('input')
        field_names = [input.get('name', f'input-{j}') for j, input in enumerate(inputs)]

        # Try to interact with the form
        try:
            if form_id:
                form_element = driver.find_element(By.ID, form_id)
            else:
                # Fallback to finding the form by action if ID is not available
                form_element = driver.find_element(By.XPATH, f"//form[@action='{form_action}']")

            # Fill in form inputs
            for input_field in inputs:
                field_name = input_field.get('name')
                if field_name:
                    input_element = form_element.find_element(By.NAME, field_name)
                    input_element.clear()
                    input_element.send_keys('test')  # Placeholder test data

            # Submit the form
            form_element.submit()
            WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
            status = 'success'
        except Exception as e:
            status = f'error: {str(e)}'

        form_info = {
            "form_id": form_id,
            "form_action": form_action,
            "description": f"Form with fields: {', '.join(field_names)}",
            "status": status
        }
        form_data.append(form_info)
    return form_data


def analyze_buttons(driver, buttons):
    button_data = []
    for i, button in enumerate(buttons):
        button_text = button.get_text(strip=True) or f'button-{i}'
        button_id = button.get('id')

        try:
            # Attempt to find and click the button by its ID or fallback to XPath using text
            if button_id:
                button_element = driver.find_element(By.ID, button_id)
            else:
                button_element = driver.find_element(By.XPATH, f"//button[text()='{button_text}']")

            button_element.click()

            try:
                # Check for alerts
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()  # Handle the alert
                status = 'alert handled'
            except NoAlertPresentException:
                status = 'no alert present'

            WebDriverWait(driver, 5).until(EC.url_changes(driver.current_url))
        except NoSuchElementException:
            status = 'error: button not found'
        except TimeoutException:
            status = 'error: timeout waiting for URL change'
        except Exception as e:
            status = f'error: {str(e)}'

        button_info = {
            "button_text": button_text,
            "button_id": button_id,
            "description": f"Button labeled '{button_text}' with ID '{button_id or 'N/A'}'",
            "status": status
        }
        button_data.append(button_info)
    return button_data


def analyze_links(driver, links):
    link_data = []
    for i, link in enumerate(links):
        link_text = link.get_text(strip=True) or f'link-{i}'
        href = link.get('href', '#')

        # Skip if the href is empty or defaults to '#'
        if href == '#' or not href.strip():
            continue

        try:
            # Find the link by its href instead of relying solely on text
            link_element = driver.find_element(By.XPATH, f"//a[@href='{href}']")
            link_element.click()
            WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
            status = 'success'
        except Exception as e:
            status = f'error: {str(e)}'

        link_info = {
            "link_text": link_text,
            "href": href,
            "description": f"Link pointing to '{href}'",
            "status": status
        }
        link_data.append(link_info)
    return link_data


def store_features_in_db(web_application, features):
    for feature_type, feature_list in features.items():
        for feature in feature_list:
            new_feature = Feature.objects.create(
                web_application=web_application,
                name=feature_type.capitalize(),
                description=feature['description']
            )
            # Generate Test Scenario and Test Case
            generate_test_scenario(web_application, new_feature)
            generate_test_case(web_application, new_feature)


def generate_test_scenario(web_application, feature):
    driver = webdriver.Chrome()
    driver.get(web_application.url)

    # Dynamically generate scenario description and purpose based on feature
    if feature.name.lower() == "forms":
        forms = driver.find_elements(By.TAG_NAME, 'form')
        if not forms:
            driver.quit()
            return

        form = forms[0]  # First form found
        description = f"Validating form '{form.get_attribute('name')}' submission."
        purpose = f"Ensure that form '{form.get_attribute('name')}' handles input data and submission correctly."

    elif feature.name.lower() == "buttons":
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        if not buttons:
            driver.quit()
            return

        button = buttons[0]  # First button found
        description = f"Testing button '{button.text}' functionality."
        purpose = f"Ensure button '{button.text}' performs the intended action when clicked."

    elif feature.name.lower() == "links":
        links = driver.find_elements(By.TAG_NAME, 'a')
        if not links:
            driver.quit()
            return

        link = links[0]  # First link found
        description = f"Testing navigation for link '{link.text}' leading to '{link.get_attribute('href')}'."
        purpose = f"Ensure link '{link.text}' navigates to the correct destination."

    else:
        description = f"Testing {feature.name} functionality."
        purpose = f"Validate the behavior of {feature.name}."

    scenario_id = f"TS_{feature.name.upper()}_{feature.id}"

    # Create the Test Scenario
    TestScenario.objects.create(
        web_application=web_application,
        feature=feature,
        scenario_id=scenario_id,
        description=description,
        purpose=purpose
    )

    driver.quit()


def generate_test_case(web_application, feature):
    driver = webdriver.Chrome()
    driver.get(web_application.url)

    scenario = TestScenario.objects.filter(web_application=web_application, feature=feature).first()
    if not scenario:
        driver.quit()
        return  # Scenario should be generated first

    if feature.name.lower() == "forms":
        forms = driver.find_elements(By.TAG_NAME, 'form')
        if not forms:
            driver.quit()
            return

        form = forms[0]
        form_name = form.get_attribute('name')

        # Dynamically generated test case for forms
        test_case_id = f"TC_FORM_{feature.id}_001"
        description = f"Verify that the form '{form_name}' submits correctly with valid data."
        pre_conditions = f"The form '{form_name}' is visible and accessible on the page."
        test_steps = (
            f"1. Fill out the form '{form_name}' with valid data.\n"
            "2. Submit the form.\n"
            "3. Verify the submission response."
        )
        test_data = "Input valid data in the form fields."
        expected_result = "Form is submitted successfully, and user receives confirmation."
        post_conditions = "Form data is saved correctly, and user remains on the correct page."
        priority = "High"

    elif feature.name.lower() == "buttons":
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        if not buttons:
            driver.quit()
            return

        button = buttons[0]
        button_text = button.text

        # Dynamically generated test case for buttons
        test_case_id = f"TC_BUTTON_{feature.id}_001"
        description = f"Verify that the button '{button_text}' performs its intended action."
        pre_conditions = f"The button '{button_text}' is visible and clickable."
        test_steps = (
            f"1. Click the button '{button_text}'.\n"
            "2. Observe the resulting action."
        )
        test_data = "No specific data required."
        expected_result = f"Button '{button_text}' performs the expected action without errors."
        post_conditions = "User is navigated or action is performed successfully."
        priority = "Medium"

    elif feature.name.lower() == "links":
        links = driver.find_elements(By.TAG_NAME, 'a')
        if not links:
            driver.quit()
            return

        link = links[0]
        link_text = link.text
        link_href = link.get_attribute('href')

        # Dynamically generated test case for links
        test_case_id = f"TC_LINK_{feature.id}_001"
        description = f"Verify that the link '{link_text}' navigates to the correct URL."
        pre_conditions = f"The link '{link_text}' is visible and clickable."
        test_steps = (
            f"1. Click the link '{link_text}'.\n"
            f"2. Verify the navigation to '{link_href}'."
        )
        test_data = "No specific data required."
        expected_result = f"User is redirected to '{link_href}' without errors."
        post_conditions = "User is on the correct target page."
        priority = "Low"

    else:
        # Default test case for unknown feature types
        test_case_id = f"TC_{feature.name.upper()}_{feature.id}_001"
        description = f"Test the functionality of '{feature.description}'."
        pre_conditions = f"{feature.name.capitalize()} is visible and functional on the page."
        test_steps = f"1. Interact with the {feature.name}.\n2. Observe its behavior."
        test_data = "Relevant data according to the feature."
        expected_result = f"{feature.name.capitalize()} functions as expected."
        post_conditions = f"{feature.name.capitalize()} remains stable."
        priority = "Medium"

    # Create the Test Case
    TestCase.objects.create(
        test_scenario=scenario,
        test_case_id=test_case_id,
        description=description,
        pre_conditions=pre_conditions,
        test_steps=test_steps,
        test_data=test_data,
        expected_result=expected_result,
        post_conditions=post_conditions,
        priority=priority,
        test_environment="Browser: Chrome, OS: Windows 10",
        test_case_type="",
        tester_name="Auto Generated",
        date=date.today()
    )

    driver.quit()


def generate_test_scenarios_and_cases_excel(test_scenarios, test_cases):
    # Create a new workbook and add sheets
    wb = openpyxl.Workbook()
    
    # Add Test Scenarios sheet
    ws_scenarios = wb.active
    ws_scenarios.title = 'Test Scenarios'

    # Add header
    headers_scenarios = [
        'Scenario ID', 'Feature Name', 'Description', 'Purpose', 'Web Application'
    ]
    ws_scenarios.append(headers_scenarios)

    # Apply bold font to header row
    for cell in ws_scenarios[1]:
        cell.font = Font(size=12, bold=True)

    # Add test scenarios data
    for scenario in test_scenarios:
        ws_scenarios.append([
            scenario.scenario_id,
            scenario.feature.name,
            scenario.description,
            scenario.purpose,
            scenario.web_application.name
        ])

    # Add Test Cases sheet
    ws_cases = wb.create_sheet(title='Test Cases')

    # Add header
    headers_cases = [
        'Test Case ID', 'Scenario ID', 'Description', 'Pre-Conditions', 'Test Steps',
        'Test Data', 'Expected Result', 'Post-Conditions', 'Priority', 'Test Environment', 'Tester Name', 'Date'
    ]
    ws_cases.append(headers_cases)

    # Apply bold font to header row
    for cell in ws_cases[1]:
        cell.font = Font(size=12, bold=True)

    # Add test cases data
    for case in test_cases:
        ws_cases.append([
            case.test_case_id,
            case.test_scenario.scenario_id,
            case.description,
            case.pre_conditions,
            case.test_steps,
            case.test_data,
            case.expected_result,
            case.post_conditions,
            case.priority,
            case.test_environment,
            case.tester_name,
            case.date
        ])

    return wb
