HR Access Control UI - Navigation Icons
Page Navigation Icons
HR Mutation Entry
Icon: person-fill
Library: Bootstrap Icons
Usage: Represents user/HR data entry
Color: Cyan (#00b8d9)
Size: 1.3em
Audit Trail
Icon: journal-text
Library: Bootstrap Icons
Usage: Represents logs, records, and audit documentation
Color: Cyan (#00b8d9)
Size: 1.3em
Icon Implementation
The icons are from the Bootstrap Icons library and are integrated via the streamlit-option-menu component.

Technical Details
selected = option_menu(
    menu_title=None,
    options=["HR Mutation Entry", "Audit Trail"],
    icons=["person-fill", "journal-text"],
    menu_icon="cast",
    default_index=0,
    styles={
        "container": {"background-color": "#0a2342", "padding": "0.5em 0.5em 2em 0.5em"},
        "icon": {"color": "#00b8d9", "font-size": "1.3em"},
        "nav-link": {"font-size": "1.1em", "color": "#fff", "margin":"0.2em 0", "border-radius": "6px"},
        "nav-link-selected": {"background-color": "#0052cc", "color": "#fff"},
    },
)
Visual Appearance
Icons appear to the left of each menu item
Active/selected state uses the primary gradient background
Icons maintain consistent cyan color for brand recognition
Smooth transitions on hover and selection
Alternative Icon Options (Bootstrap Icons)
If you need to change or add icons, here are some relevant alternatives:

For HR/User Management:
person-plus-fill - Adding users
people-fill - Multiple users/team
person-badge-fill - User credentials
person-gear - User settings
For Audit/Logging:
file-text-fill - Documents
clipboard-data-fill - Data logs
list-check - Checklist/audit items
shield-check - Security audit
graph-up - Analytics/reports
Icon Library: Bootstrap Icons (https://icons.getbootstrap.com/)
Integration: streamlit-option-menu component
Style: Filled icons for modern, bold appearance

Generated from KotP_Team12 Streamlit UI