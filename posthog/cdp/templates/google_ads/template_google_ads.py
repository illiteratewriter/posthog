from posthog.cdp.templates.hog_function_template import HogFunctionTemplate

# Based on https://developers.google.com/google-ads/api/reference/rpc/v17/ClickConversion

template: HogFunctionTemplate = HogFunctionTemplate(
    status="alpha",
    type="destination",
    id="template-google-ads",
    name="Google Ads Conversions",
    description="Send conversion events to Google Ads",
    icon_url="/static/services/google-ads.png",
    category=["Advertisement"],
    hog="""
if (empty(inputs.gclid)) {
    print('Empty `gclid`. Skipping...')
    return
}

let body := {
    'conversions': [
        {
            'gclid': inputs.gclid,
            'conversion_action': f'customers/{replaceAll(inputs.customerId, '-', '')}/conversionActions/{replaceAll(inputs.conversionActionId, 'AW-', '')}',
            'conversion_date_time': inputs.conversionDateTime
        }
    ],
    'partialFailure': true,
    'validateOnly': true
}

if (not empty(inputs.conversionValue)) {
    body.conversions[1].conversion_value := inputs.conversionValue
}
if (not empty(inputs.currencyCode)) {
    body.conversions[1].currency_code := inputs.currencyCode
}

let res := fetch(f'https://googleads.googleapis.com/v17/customers/{replaceAll(inputs.customerId, '-', '')}:uploadClickConversions', {
    'method': 'POST',
    'headers': {
        'Authorization': f'Bearer {inputs.oauth.access_token}',
        'Content-Type': 'application/json',
        'developer-token': inputs.developerToken
    },
    'body': body
})

if (res.status >= 400) {
    throw Error(f'Error from googleads.googleapis.com (status {res.status}): {res.body}')
}
""".strip(),
    inputs_schema=[
        {
            "key": "oauth",
            "type": "integration",
            "integration": "google-ads",
            "label": "Google Ads account",
            "secret": False,
            "required": True,
        },
        {
            "key": "developerToken",
            "type": "string",
            "label": "Developer token",
            "description": "This should be a 22-character long alphanumeric string. Check out this page on how to obtain such a token: https://developers.google.com/google-ads/api/docs/get-started/dev-token",
            "secret": False,
            "required": True,
        },
        {
            "key": "customerId",
            "type": "string",
            "label": "Customer ID",
            "description": "ID of your Google Ads Account. This should be 10-digits and in XXX-XXX-XXXX format.",
            "secret": False,
            "required": True,
        },
        {
            "key": "conversionActionId",
            "type": "string",
            "label": "Conversion action ID",
            "description": "You will find this information in the event snippet for your conversion action, for example send_to: AW-CONVERSION_ID/AW-CONVERSION_LABEL. This should be in the AW-CONVERSION_ID format.",
            "secret": False,
            "required": True,
        },
        {
            "key": "gclid",
            "type": "string",
            "label": "Google Click ID (gclid)",
            "description": "The Google click ID (gclid) associated with this conversion.",
            "default": "{person.properties.gclid ?? person.properties.$initial_gclid}",
            "secret": False,
            "required": True,
        },
        {
            "key": "conversionDateTime",
            "type": "string",
            "label": "Conversion Date Time",
            "description": 'The date time at which the conversion occurred. Must be after the click time. The timezone must be specified. The format is "yyyy-mm-dd hh:mm:ss+|-hh:mm", e.g. "2019-01-01 12:32:45-08:00".',
            "default": "{event.timestamp}",
            "secret": False,
            "required": True,
        },
        {
            "key": "conversionValue",
            "type": "string",
            "label": "Conversion value",
            "description": "The value of the conversion for the advertiser.",
            "default": "",
            "secret": False,
            "required": False,
        },
        {
            "key": "currencyCode",
            "type": "string",
            "label": "Currency code",
            "description": "Currency associated with the conversion value. This is the ISO 4217 3-character currency code. For example: USD, EUR.",
            "default": "",
            "secret": False,
            "required": False,
        },
    ],
    filters={
        "events": [],
        "actions": [],
        "filter_test_accounts": True,
    },
)
