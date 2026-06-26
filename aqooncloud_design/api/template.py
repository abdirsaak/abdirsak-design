import frappe 
import json
from frappe.utils import getdate
# from anfac_retail.anfac_retail.page.dashboard_page.dashboard_page import get_data
# from frappe.desk.desktop import get_workspace_sidebar_items
# import matplotlib.pyplot as plt
# from random import randrange
# import random

# @frappe.whitelist()
# def get_html():
#     data = get_data("2022-1-11" , "2022-11-20")
#     # frappe.errprint(get_balance_shet())
#     return frappe.render_template("anfac_retail/api/templates/dashboard_workspace.html", {"data" : data}) , get_prof_and_los() , get_balance_shet()
#     # return frappe.render_template("anfac_retail.anfac_retail.page.dashboard_page.dashboard_page.html", {"data" : data})
def has_role(user, role):
    roles = frappe.get_roles(user)
    return role in roles

@frappe.whitelist()
def get_workspace_sidebar_items():
	"""Get list of sidebar items for desk"""

	has_access =1
	# don't get domain restricted pages
	allowed_modules = []
	if frappe.db.exists("User Home", frappe.session.user, cache=True):
		user_page = frappe.get_doc("User Home", frappe.session.user).allowed_modules
		
		for page in user_page:
			allowed_modules.append(page.module)
	
	
	filters = {
	
		"name": ["in", allowed_modules],
		# "image_icon" :  ["!=", ""]
	}

	if frappe.session.user == "Administrator" or has_role(frappe.session.user , "Full Admin"):
		filters = {}
	
	# pages sorted based on sequence id
	# order_by = "name asc"
	order_by = "sequence_id asc,name asc"
    # order_by = "sequence_id asc, name asc"
	fields = ["name", "label", 'color',  "module", "icon", "image_icon"]
	all_pages = frappe.get_all(
		"Home Page", fields=fields, filters=filters, order_by=order_by, ignore_permissions=True
	)
	pages = []
	private_pages = []

	# Filter Page based on Permission
	# for page in all_pages:
	# 	try:
	# 		workspace = Workspace(page, True)
	# 		if has_access or workspace.is_permitted():
	# 			if page.public:
	# 				pages.append(page)
	# 			elif page.for_user == frappe.session.user:
	# 				private_pages.append(page)
	# 			page["label"] = _(page.get("name"))
	# 	except frappe.PermissionError:
	# 		pass
	# if private_pages:
	# 	pages.extend(private_pages)

	return {"pages": all_pages, "has_access": has_access}


@frappe.whitelist()
def app_page():
	# data = get_data("2022-1-11" , "2022-11-20")
	# frappe.errprint(get_balance_shet())
	data = get_workspace_sidebar_items()['pages']
	# frappe.errprint(data)
	# return frappe.render_template("aqooncloud_design/api/templates/new_app_page.html", {"data" : data})  , "test"


	renderedTemplate = frappe.render_template("aqooncloud_design/api/templates/new_app_page.html", {"data" : data});

	return [renderedTemplate,data]

	# return frappe.render_template("anfac_retail.anfac_retail.page.dashboard_page.dashboard_page.html", {"data" : data})



@frappe.whitelist()
def can_user_see_notifications():
    """
    Checks if any of the current user's roles have the 'enable_search' field checked.
    Returns True if at least one role has the permission, otherwise False.
    """
    user_roles = frappe.get_roles()

    # Check if any of the user's roles have enable_search enabled
    roles_with_permission = frappe.get_all('Role', 
        filters={
            'name': ['in', user_roles],
            # 'enable_search': 1
        },
        limit=1
    )
    
    return bool(roles_with_permission)


@frappe.whitelist()
def get_shortcut_counts(shortcuts):
    """
    Accepts a list of shortcuts (as stringified JSON), calculates counts for those
    with a valid stats_filter, and returns a dictionary of counts.
    """
    counts = {}
    # The shortcuts argument will come from JS as a JSON string
    shortcut_list = json.loads(shortcuts)

    for shortcut in shortcut_list:
        # Check if the necessary keys exist and stats_filter has a value
        if shortcut.get('link_to') and shortcut.get('stats_filter'):
            try:
                # Parse the filter string into a Python dictionary
                filters = json.loads(shortcut['stats_filter'])
                
                # Use frappe.db.count to get the count
                count = frappe.db.count(shortcut['link_to'], filters)
                
                # Only add to the dictionary if the count is greater than zero
                if count > 0:
                    # Use the 'link_to' as a unique key for the count
                    counts[shortcut['link_to']] = count
            except (json.JSONDecodeError, TypeError):
                # Ignore shortcuts with invalid JSON in their filter
                pass
    
    return counts


    
    
@frappe.whitelist()
def get_company_logo(company_name = None):
    """
    Get company logo with multiple fallback options
    """
    
    if not company_name:
        return None
    
    try:
        # 1. Try to get logo from Company doctype
        company_logo = frappe.db.get_value("Company", company_name, "company_logo")
        
        if company_logo:
            return company_logo
        
        # 2. Check if there's a default logo in Website Settings
        website_logo = frappe.db.get_single_value("Website Settings", "brand_html") 
        # or check other logo fields in Website Settings
        
        # 3. Check for favicon or app logo as fallback
        app_logo = frappe.db.get_single_value("Website Settings", "app_logo")
        
        return company_logo or app_logo or website_logo
        
    except Exception:
        frappe.log_error("Error getting company logo")
        return None    