import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="CoreBank Legacy Servicing Portal")

MEMBERS_DB = {
    "12345": {
        "name": "Sarah Connor",
        "ssn": "987-65-4321",
        "savings_balance": "$14,850.25",
        "checking_balance": "$2,120.00",
        "status": "Active",
        "tier": "Platinum Commercial"
    },
    "67890": {
        "name": "John Doe",
        "ssn": "123-45-6789",
        "savings_balance": "$540.10",
        "checking_balance": "$12.50",
        "status": "Active",
        "tier": "Standard Retail"
    },
    "99999": {
        "name": "Miles Dyson",
        "ssn": "555-01-9922",
        "savings_balance": "$0.00",
        "checking_balance": "$0.00",
        "status": "Frozen",
        "tier": "Restricted"
    }
}

HTML_SHELL = """
<!DOCTYPE html>
<html>
<head>
    <title>CoreBank Servicing Mainframe v4.8</title>
    <style>
        body {{ font-family: 'Courier New', Courier, monospace; background: #c0c0c0; margin: 20px; color: #000; }}
        .window {{ background: #fff; border: 3px outset #dfdfdf; padding: 12px; width: 720px; box-shadow: 6px 6px #404040; }}
        .titlebar {{ background: #000080; color: #fff; padding: 4px 8px; font-weight: bold; margin-bottom: 12px; display: flex; justify-content: space-between; }}
        .nav {{ background: #e0e0e0; border: 1px solid #808080; padding: 6px; margin-bottom: 15px; }}
        .nav a {{ margin-right: 15px; color: #000080; font-weight: bold; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        td, th {{ border: 1px solid #808080; padding: 5px; text-align: left; }}
        th {{ background: #d0d0d0; }}
        .btn {{ background: #c0c0c0; border: 2px outset #ffffff; padding: 4px 10px; font-weight: bold; cursor: pointer; font-family: inherit; }}
        .btn:active {{ border: 2px inset #ffffff; }}
        .alert-error {{ background: #ffcccc; border: 2px solid #cc0000; padding: 8px; color: #990000; margin-top: 12px; font-weight: bold; }}
        .alert-warning {{ background: #fff3cd; border: 2px solid #ffeeba; padding: 8px; color: #856404; margin-top: 12px; font-weight: bold; }}
        .badge-active {{ color: green; font-weight: bold; }}
        .badge-frozen {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="window">
        <div class="titlebar">
            <span>CORE-BANK MAINFRAME // TERMINAL [NODE_US_EAST_04]</span>
            <span>SECURE SESSION</span>
        </div>
        <div class="nav">
            <a href="/" id="nav-home">[Dashboard]</a>
            <a href="/members/search" id="nav-member-search" role="link">[Member Lookup]</a>
            <a href="/transfers" id="nav-transfers" role="link">[Funds Transfer]</a>
        </div>
        {content}
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_SHELL.format(content="""
        <h3>OPERATOR CONSOLE: ACTIVE</h3>
        <p>Authenticated Operator ID: <strong>OP-9942-SYS</strong></p>
        <p>System State: <em>NORMAL_PRODUCTION</em></p>
        <p>Select an administrative function from the navigation menu above.</p>
    """)

@app.get("/members/search", response_class=HTMLResponse)
def member_search_form():
    return HTML_SHELL.format(content="""
        <h3>MEMBER SERVICING: ACCOUNT QUERY</h3>
        <form method="post" action="/members/search">
            <table style="border: none;">
                <tr>
                    <td style="border: none; width: 180px;"><label for="member_id">Target Member ID:</label></td>
                    <td style="border: none;">
                        <input type="text" id="member_id" name="member_id" role="textbox" aria-label="Target Member ID" style="width: 180px;" autofocus autocomplete="off" />
                    </td>
                </tr>
            </table>
            <br>
            <button type="submit" id="btn-submit-search" class="btn" role="button" name="action_lookup">Execute Query</button>
        </form>
    """)

@app.post("/members/search", response_class=HTMLResponse)
def member_search_submit(member_id: str = Form(...)):
    mid = member_id.strip()
    if mid in MEMBERS_DB:
        member = MEMBERS_DB[mid]
        badge_cls = "badge-active" if member["status"] == "Active" else "badge-frozen"
        content = f"""
            <h3>ACCOUNT RECORD RETRIEVED: {member['name']}</h3>
            <table>
                <tr><th style="width: 200px;">Data Field</th><th>Record Value</th></tr>
                <tr><td>Institution Identifier</td><td id="member-id-display">{mid}</td></tr>
                <tr><td>Full Legal Name</td><td id="member-name">{member['name']}</td></tr>
                <tr><td>Taxpayer ID (SSN)</td><td id="member-ssn">{member['ssn']}</td></tr>
                <tr><td>Account Status</td><td id="member-status"><span class="{badge_cls}">{member['status']}</span></td></tr>
                <tr><td>Classification Tier</td><td id="member-tier">{member['tier']}</td></tr>
                <tr><td>Primary Checking Balance</td><td id="checking-balance-val">{member['checking_balance']}</td></tr>
                <tr><td>Primary Savings Balance</td><td id="savings-balance-val">{member['savings_balance']}</td></tr>
            </table>
            <br>
            <a href="/members/search" class="btn" id="btn-new-search">New Search</a>
        """
        return HTML_SHELL.format(content=content)
    else:
        content = f"""
            <h3>MEMBER SERVICING: ACCOUNT QUERY</h3>
            <div class="alert-error" id="error-banner" role="alert">
                ERROR 404: Member record '{mid}' does not exist in institution core records.
            </div>
            <br>
            <a href="/members/search" class="btn" id="btn-retry-search">Back to Search</a>
        """
        return HTML_SHELL.format(content=content)

@app.get("/transfers", response_class=HTMLResponse)
def transfer_form():
    return HTML_SHELL.format(content="""
        <h3>FUNDS TRANSFER AUTHORIZATION (IRREVERSIBLE)</h3>
        <form method="post" action="/transfers/confirm">
            <table style="border: none;">
                <tr><td style="border: none;">Source Account ID:</td><td style="border: none;"><input type="text" id="src_acc" name="src_acc" style="width: 160px;"/></td></tr>
                <tr><td style="border: none;">Destination Account ID:</td><td style="border: none;"><input type="text" id="dst_acc" name="dst_acc" style="width: 160px;"/></td></tr>
                <tr><td style="border: none;">Transfer Amount ($):</td><td style="border: none;"><input type="text" id="amount" name="amount" style="width: 160px;"/></td></tr>
            </table>
            <br>
            <button type="submit" id="btn-transfer-stage" class="btn">Stage Transfer</button>
        </form>
    """)

@app.post("/transfers/confirm", response_class=HTMLResponse)
def transfer_confirm(src_acc: str = Form(...), dst_acc: str = Form(...), amount: str = Form(...)):
    return HTML_SHELL.format(content=f"""
        <h3>CONFIRMATION REQUIRED: SUBMIT TRANSACTION</h3>
        <div class="alert-warning" id="confirmation-dialog">
            WARNING: You are about to initiate an irreversible ACH settlement of ${amount} from {src_acc} to {dst_acc}.
        </div>
        <br>
        <form method="post" action="/transfers/execute">
            <input type="hidden" name="src_acc" value="{src_acc}"/>
            <input type="hidden" name="dst_acc" value="{dst_acc}"/>
            <input type="hidden" name="amount" value="{amount}"/>
            <button type="submit" id="btn-transfer-execute" class="btn" style="color: red;">COMMIT WIRE TRANSFER</button>
            <a href="/transfers" class="btn">Cancel</a>
        </form>
    """)

@app.post("/transfers/execute", response_class=HTMLResponse)
def transfer_execute(src_acc: str = Form(...), dst_acc: str = Form(...), amount: str = Form(...)):
    return HTML_SHELL.format(content=f"""
        <h3>TRANSACTION SETTLED</h3>
        <p id="tx-success">Successfully wired ${amount} to {dst_acc}. Reference ID: <strong>TXN-88492019</strong></p>
        <a href="/" class="btn">Return Home</a>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")