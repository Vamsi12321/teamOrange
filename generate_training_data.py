"""
Generate 2000+ High-Quality CCPA Training Examples
Multi-label classification with diverse phrasings and edge cases
"""

import json
import random

# CCPA Section mapping
SECTION_LABELS = [
    "Section 1798.100",  # Notice
    "Section 1798.105",  # Deletion
    "Section 1798.106",  # Correction
    "Section 1798.110",  # Disclosure of collection
    "Section 1798.115",  # Disclosure of sale/sharing
    "Section 1798.120",  # Opt-out
    "Section 1798.121",  # Sensitive data
    "Section 1798.125",  # Non-discrimination
    "Section 1798.130",  # Response time
    "Section 1798.135",  # Do Not Sell link
]

# Template patterns for each section
VIOLATION_TEMPLATES = {
    "Section 1798.100": [
        # Notice violations - must inform before collecting
        "We {collect_verb} {data_type} without {notice_verb} users",
        "Users are not {notice_verb} about our {collection_activity}",
        "{data_type} is {collect_verb} without prior {notice_noun}",
        "We don't {notice_verb} consumers before {collect_verb} their {data_type}",
        "No {notice_noun} is provided about {collection_activity}",
        "{collection_activity} happens without {notice_verb} users",
        "We {collect_verb} {data_type} {secretly_adverb}",
        "Consumers are unaware of our {collection_activity}",
        "We fail to {notice_verb} users about {data_type} {collection_activity}",
        "{data_type} is obtained without consumer {consent_noun}",
    ],
    
    "Section 1798.105": [
        # Deletion violations - must honor deletion requests
        "We {refuse_verb} to {delete_verb} {data_type} when {request_verb}",
        "{deletion_requests} are {ignore_verb}",
        "We {keep_verb} {data_type} {forever_adverb} even after {deletion_requests}",
        "Users cannot {delete_verb} their {data_type}",
        "{data_type} is {retain_verb} {permanently_adverb} despite {deletion_requests}",
        "We don't {delete_verb} {data_type} when users {request_verb}",
        "{deletion_requests} are {deny_verb}",
        "We make it {impossible_adj} to {delete_verb} {data_type}",
        "{data_type} remains in our system {forever_adverb}",
        "We {refuse_verb} all {deletion_requests}",
    ],
    
    "Section 1798.106": [
        # Correction violations - must allow correction
        "We {refuse_verb} to {correct_verb} {inaccurate_adj} {data_type}",
        "Users cannot {correct_verb} their {data_type}",
        "{correction_requests} are {ignore_verb}",
        "We don't allow {correction_noun} of {inaccurate_adj} {data_type}",
        "There is no way to {update_verb} {data_type}",
        "{correction_requests} are {deny_verb}",
        "We {refuse_verb} to {fix_verb} {incorrect_adj} information",
        "{inaccurate_adj} {data_type} cannot be {correct_verb}",
        "We don't {respond_verb} to {correction_requests}",
        "Users have no ability to {correct_verb} {data_type}",
    ],
    
    "Section 1798.110": [
        # Disclosure violations - must disclose what's collected
        "We don't {disclose_verb} what {data_type} we {collect_verb}",
        "Users cannot {find_out_verb} what {data_type} we have",
        "We {refuse_verb} to {tell_verb} consumers what {data_type} we {collect_verb}",
        "Our {policy_noun} doesn't list {collected_data}",
        "We {hide_verb} what {data_type} we {gather_verb}",
        "Consumers cannot {access_verb} their {collected_data}",
        "We don't provide information about {collection_activity}",
        "Users have no way to {see_verb} what we {collect_verb}",
        "We {refuse_verb} {disclosure_requests}",
        "{data_type} {collection_activity} is not {disclose_verb}",
    ],
    
    "Section 1798.115": [
        # Sale/sharing disclosure violations
        "We don't {disclose_verb} that we {sell_verb} {data_type}",
        "We {share_verb} {data_type} with {third_parties} without {disclosure_noun}",
        "Users don't know we {sell_verb} their {data_type}",
        "We {hide_verb} the fact that we {share_verb} {data_type}",
        "Our {policy_noun} doesn't mention {data_sales}",
        "We {sell_verb} {data_type} to {third_parties} without {tell_verb} users",
        "{third_party_sharing} is not {disclose_verb}",
        "We don't {inform_verb} consumers about {data_monetization}",
        "{data_sales} are kept {secret_adj}",
        "We {fail_verb} to {disclose_verb} {third_party_sharing}",
    ],
    
    "Section 1798.120": [
        # Opt-out violations
        "Users cannot {opt_out_verb} of {data_sales}",
        "We don't allow {opt_out_noun} of {data_sharing}",
        "{opt_out_noun} is not {available_adj} for consumers",
        "We make it {difficult_adj} to {opt_out_verb}",
        "The {opt_out_process} is {complicated_adj}",
        "There is no way to {stop_verb} {data_sales}",
        "We {sell_verb} {data_type} without {opt_out_option}",
        "{opt_out_noun} requires {complex_process}",
        "We {ignore_verb} {opt_out_requests}",
        "Users must {pay_verb} to {opt_out_verb}",
    ],
    
    "Section 1798.121": [
        # Sensitive data violations
        "We {sell_verb} {data_type} of {minors} without {consent_noun}",
        "We {share_verb} {sensitive_data} of users under {age}",
        "{children_data} is {sell_verb} to {third_parties}",
        "We {sell_verb} {geolocation_data} without {permission_noun}",
        "We {process_verb} {sensitive_data} without {consent_noun}",
        "{health_data} is {share_verb} without {authorization_noun}",
        "We {collect_verb} {biometric_data} from {minors}",
        "{precise_location} is {track_verb} without {opt_in_noun}",
        "We use {sensitive_data} for {profiling_noun} without {consent_noun}",
        "{children_data} is {process_verb} without {parental_consent}",
    ],
    
    "Section 1798.125": [
        # Discrimination violations
        "We {charge_verb} {higher_prices} to users who {opt_out_verb}",
        "Users who {exercise_rights} {pay_verb} more",
        "We {discriminate_verb} against consumers who {opt_out_verb}",
        "{premium_users} get {better_service} if they don't {opt_out_verb}",
        "We {penalize_verb} users for {exercise_rights}",
        "{opt_out_verb} {reduce_verb} {service_quality}",
        "Users who {delete_data} lose {access_noun} to {features}",
        "We offer {discounts} only to users who allow {data_sales}",
        "{privacy_users} get {slower_support}",
        "We {deny_verb} {service_noun} to users who {opt_out_verb}",
    ],
    
    "Section 1798.130": [
        # Response time violations
        "We never {respond_verb} to {privacy_requests}",
        "We {ignore_verb} all {privacy_requests}",
        "{consumer_requests} are not {answer_verb}",
        "We don't {respond_verb} to {data_requests}",
        "{privacy_requests} take {months} to {process_verb}",
        "We take {90_days} to {respond_verb} to {requests}",
        "{requests} are {delay_verb} {indefinitely}",
        "We don't meet the {45_day_deadline}",
        "{consumer_requests} sit in {queue} for {weeks}",
        "We rarely {respond_verb} within the {required_timeframe}",
    ],
    
    "Section 1798.135": [
        # Do Not Sell link violations
        "Our {website} has no {do_not_sell_link}",
        "There is no {do_not_sell_option}",
        "We don't have an {opt_out_link} on our {site}",
        "The {do_not_sell_link} is {hidden_adj} in {footer}",
        "We {remove_verb} the {do_not_sell_button}",
        "Our {homepage} doesn't have a {do_not_sell_link}",
        "The {opt_out_link} is not {clearly_labeled}",
        "We don't provide a {do_not_sell_link}",
        "{do_not_sell_link} is {difficult_to_find}",
        "Our {website} lacks the required {do_not_sell_link}",
    ],
}

# Vocabulary for template filling
VOCABULARY = {
    "collect_verb": ["collect", "gather", "obtain", "acquire", "capture", "harvest", "track", "monitor", "record", "extract"],
    "data_type": ["personal information", "user data", "consumer data", "personal data", "information", "data", "user information", "consumer information", "private data", "sensitive information"],
    "notice_verb": ["informing", "notifying", "telling", "alerting", "disclosing to", "warning", "advising", "communicating to"],
    "notice_noun": ["notice", "notification", "disclosure", "warning", "information", "communication", "alert"],
    "collection_activity": ["data collection", "information gathering", "data harvesting", "tracking", "monitoring", "data capture"],
    "secretly_adverb": ["secretly", "quietly", "covertly", "without disclosure", "without notice", "implicitly", "automatically", "in the background"],
    "consent_noun": ["knowledge", "consent", "permission", "authorization", "approval", "awareness"],
    
    "refuse_verb": ["refuse", "decline", "reject", "deny", "fail", "won't", "don't"],
    "delete_verb": ["delete", "remove", "erase", "purge", "eliminate", "destroy"],
    "request_verb": ["requested", "asked", "demanded", "required"],
    "deletion_requests": ["deletion requests", "removal requests", "erasure requests", "data deletion requests", "requests to delete"],
    "ignore_verb": ["ignored", "dismissed", "disregarded", "overlooked", "neglected"],
    "keep_verb": ["keep", "retain", "store", "hold", "maintain", "preserve"],
    "forever_adverb": ["forever", "permanently", "indefinitely", "always", "eternally"],
    "retain_verb": ["retained", "kept", "stored", "held", "maintained", "preserved"],
    "permanently_adverb": ["permanently", "indefinitely", "forever", "always"],
    "deny_verb": ["denied", "rejected", "refused", "declined"],
    "impossible_adj": ["impossible", "very difficult", "extremely hard", "nearly impossible"],
    
    "correct_verb": ["correct", "fix", "update", "amend", "modify", "change"],
    "inaccurate_adj": ["inaccurate", "incorrect", "wrong", "erroneous", "false"],
    "correction_requests": ["correction requests", "requests to correct", "amendment requests", "update requests"],
    "correction_noun": ["correction", "amendment", "modification", "updating"],
    "update_verb": ["update", "modify", "change", "amend", "fix"],
    "fix_verb": ["fix", "correct", "repair", "amend"],
    "incorrect_adj": ["incorrect", "wrong", "inaccurate", "erroneous"],
    "respond_verb": ["respond", "reply", "answer"],
    
    "disclose_verb": ["disclose", "reveal", "tell", "inform about", "communicate"],
    "find_out_verb": ["find out", "discover", "learn", "see", "know"],
    "tell_verb": ["tell", "inform", "notify", "disclose to"],
    "policy_noun": ["privacy policy", "policy", "terms", "documentation"],
    "collected_data": ["collected data", "gathered information", "stored data"],
    "hide_verb": ["hide", "conceal", "obscure", "withhold"],
    "gather_verb": ["gather", "collect", "obtain"],
    "access_verb": ["access", "view", "see", "retrieve"],
    "see_verb": ["see", "view", "access", "review"],
    "disclosure_requests": ["disclosure requests", "access requests", "information requests"],
    
    "sell_verb": ["sell", "monetize", "commercialize", "trade"],
    "share_verb": ["share", "distribute", "provide", "give"],
    "third_parties": ["third parties", "advertisers", "partners", "vendors", "brokers"],
    "disclosure_noun": ["disclosure", "notice", "notification", "informing users"],
    "data_sales": ["data sales", "selling data", "data monetization"],
    "inform_verb": ["inform", "tell", "notify", "disclose to"],
    "third_party_sharing": ["third-party sharing", "data sharing", "information sharing"],
    "data_monetization": ["data monetization", "selling data", "data sales"],
    "secret_adj": ["secret", "hidden", "undisclosed", "concealed"],
    "fail_verb": ["fail", "neglect", "omit"],
    
    "opt_out_verb": ["opt out", "opt-out", "unsubscribe", "withdraw"],
    "data_sales": ["data sales", "selling data", "data monetization"],
    "opt_out_noun": ["opt-out", "opting out", "withdrawal"],
    "data_sharing": ["data sharing", "information sharing", "data distribution"],
    "available_adj": ["available", "possible", "offered", "provided"],
    "difficult_adj": ["extremely difficult", "very hard", "nearly impossible", "complicated"],
    "opt_out_process": ["opt-out process", "unsubscribe process", "withdrawal process"],
    "complicated_adj": ["very complicated", "extremely complex", "confusing", "difficult"],
    "stop_verb": ["stop", "prevent", "halt", "end"],
    "opt_out_option": ["opt-out option", "way to opt out", "unsubscribe option"],
    "complex_process": ["multiple steps", "complex verification", "many hoops", "difficult procedures"],
    "opt_out_requests": ["opt-out requests", "unsubscribe requests", "withdrawal requests"],
    "pay_verb": ["pay", "pay a fee", "subscribe"],
    
    "minors": ["minors", "children", "kids under 16", "users under 16"],
    "sensitive_data": ["sensitive information", "sensitive data", "private information"],
    "age": ["16", "18", "13"],
    "children_data": ["children's data", "minors' data", "kids' information"],
    "geolocation_data": ["geolocation data", "location data", "GPS data", "precise location"],
    "permission_noun": ["permission", "consent", "authorization"],
    "process_verb": ["process", "use", "handle"],
    "health_data": ["health data", "medical information", "health records"],
    "authorization_noun": ["authorization", "consent", "permission"],
    "biometric_data": ["biometric data", "fingerprints", "facial recognition data"],
    "precise_location": ["precise location", "exact location", "GPS coordinates"],
    "track_verb": ["tracked", "monitored", "recorded"],
    "opt_in_noun": ["opt-in", "explicit consent", "permission"],
    "profiling_noun": ["profiling", "targeting", "analysis"],
    "parental_consent": ["parental consent", "parent permission", "guardian authorization"],
    
    "charge_verb": ["charge", "bill", "invoice"],
    "higher_prices": ["higher prices", "more money", "premium fees", "extra charges"],
    "exercise_rights": ["exercise privacy rights", "use their rights", "request privacy"],
    "discriminate_verb": ["discriminate", "penalize", "punish"],
    "premium_users": ["premium users", "paying users", "subscribers"],
    "better_service": ["better service", "faster support", "more features"],
    "penalize_verb": ["penalize", "punish", "disadvantage"],
    "reduce_verb": ["reduces", "degrades", "lowers"],
    "service_quality": ["service quality", "features", "functionality"],
    "delete_data": ["delete data", "remove information", "erase records"],
    "access_noun": ["access", "ability to use"],
    "features": ["features", "functionality", "services"],
    "discounts": ["discounts", "lower prices", "special offers"],
    "privacy_users": ["privacy-conscious users", "users who opt out", "privacy advocates"],
    "slower_support": ["slower support", "delayed service", "lower priority"],
    "deny_verb": ["deny", "refuse", "reject"],
    "service_noun": ["service", "access", "functionality"],
    
    "privacy_requests": ["privacy requests", "consumer requests", "data requests"],
    "consumer_requests": ["consumer requests", "user requests", "privacy requests"],
    "answer_verb": ["answered", "responded to", "addressed"],
    "data_requests": ["data requests", "information requests", "privacy requests"],
    "months": ["months", "many weeks", "a long time"],
    "process_verb": ["process", "handle", "complete"],
    "90_days": ["90 days", "three months", "many weeks"],
    "requests": ["requests", "inquiries", "demands"],
    "delay_verb": ["delayed", "postponed", "put off"],
    "indefinitely": ["indefinitely", "forever", "without timeline"],
    "45_day_deadline": ["45-day deadline", "required timeframe", "legal deadline"],
    "queue": ["queue", "backlog", "waiting list"],
    "weeks": ["weeks", "many days", "a long time"],
    "required_timeframe": ["required timeframe", "legal deadline", "45-day window"],
    
    "website": ["website", "site", "platform", "homepage"],
    "do_not_sell_link": ["Do Not Sell link", "Do Not Sell My Personal Information link", "opt-out link"],
    "do_not_sell_option": ["Do Not Sell My Personal Information option", "Do Not Sell option", "opt-out option"],
    "opt_out_link": ["opt-out link", "Do Not Sell link", "unsubscribe link"],
    "site": ["site", "website", "platform"],
    "hidden_adj": ["hidden", "buried", "obscured"],
    "footer": ["footer", "bottom of page", "fine print"],
    "remove_verb": ["removed", "deleted", "eliminated"],
    "do_not_sell_button": ["Do Not Sell button", "opt-out button", "privacy button"],
    "homepage": ["homepage", "main page", "landing page"],
    "clearly_labeled": ["clearly labeled", "easy to find", "prominent"],
    "difficult_to_find": ["difficult to find", "hard to locate", "hidden"],
}

# Safe practice templates - MASSIVELY EXPANDED
SAFE_TEMPLATES = [
    # Compliant practices
    "We provide clear privacy notices before collecting data",
    "We honor all deletion requests within 45 days",
    "Users can easily opt out of data sales",
    "We do not discriminate against users who exercise privacy rights",
    "Our website has a prominent Do Not Sell My Personal Information link",
    "We respond to all consumer requests promptly",
    "We allow users to correct their personal information",
    "We obtain parental consent before collecting data from minors",
    "We disclose all data collection practices in our privacy policy",
    "We provide free opt-out mechanisms for all users",
    "Users can delete their accounts and all associated data",
    "We inform consumers about data collection before it happens",
    "Privacy rights are easy to exercise on our platform",
    "We respect all consumer privacy choices",
    "Data deletion is simple and fast",
    "We don't sell personal information",
    "Consumer data is protected and not shared",
    "We comply with all CCPA requirements",
    "Privacy is our top priority",
    "We give users full control over their data",
    "Our privacy policy is clear and comprehensive",
    "We process data transparently and fairly",
    "Users have full access to their personal information",
    "We respond to privacy requests within 10 days",
    "All user rights are clearly explained and easy to exercise",
    "We never sell or share personal data",
    "Our Do Not Sell link is prominently displayed",
    "We obtain explicit consent for all data processing",
    "Privacy settings are user-friendly and accessible",
    "We maintain strict data protection standards",
    
    # CRITICAL: Neutral collection statements (NOT violations)
    "We collect personal information from customers",
    "We take personal info of customers",
    "We are taking personal information",
    "We gather customer data",
    "We obtain user information",
    "We process customer data",
    "We store user information",
    "We use customer data",
    "We collect data from users",
    "We gather information from customers",
    "Personal information is collected",
    "Customer data is processed",
    "We maintain customer records",
    "User data is stored in our systems",
    "We handle personal information",
    "We collect customer information for business purposes",
    "We gather data to improve our services",
    "We obtain information from users during registration",
    "We process personal data for analytics",
    "We store customer data securely",
    "We use personal information to provide services",
    "We collect data when you use our website",
    "We gather information through cookies",
    "We obtain data from third-party sources",
    "We process information to fulfill orders",
    
    # Security statements (NOT CCPA violations - CCPA doesn't regulate security)
    "We encrypt all stored personal data",
    "User passwords are hashed and salted",
    "We use SSL/TLS for data transmission",
    "We implement industry-standard security measures",
    "We protect personal information with encryption",
    "We secure data using advanced encryption",
    "We store passwords securely",
    "We use secure protocols for data transmission",
    "We implement multi-factor authentication",
    "We conduct regular security audits",
    "We have a data breach response plan",
    "We monitor systems for security threats",
    "We use firewalls to protect data",
    "We limit access to personal information",
    "We train employees on data security",
    "We do not guarantee encryption of stored personal data",
    "User passwords may be stored in plain text",
    "We are not responsible for protecting your personal information",
    "Sensitive data may be transmitted without secure protocols",
    "We do not encrypt all data",
    "We cannot guarantee complete security",
    "Data breaches may occur",
    "We are not liable for security incidents",
    "Third parties may access your data",
    "We use standard security practices",
    
    # Business operations (neutral - NOT violations)
    "We share data with service providers",
    "We use third-party analytics tools",
    "We work with vendors to process data",
    "We partner with other companies",
    "We use cloud storage for data",
    "We employ data processors",
    "We engage contractors for data handling",
    "We utilize third-party services",
    "We collaborate with business partners",
    "We outsource some data processing",
    
    # Marketing and analytics (neutral if disclosed)
    "We use data for marketing purposes",
    "We analyze customer behavior",
    "We track website usage",
    "We use cookies for analytics",
    "We personalize user experiences",
    "We send promotional emails",
    "We use data for advertising",
    "We create customer profiles",
    "We segment our audience",
    "We measure campaign effectiveness",
    
    # Data retention (neutral if disclosed)
    "We retain data for business purposes",
    "We keep records for legal compliance",
    "We store data for the duration of your account",
    "We maintain historical data",
    "We archive old records",
    "We preserve data as required by law",
    "We keep transaction history",
    "We retain data for customer service",
    "We store data for fraud prevention",
    "We maintain backup copies",
    
    # Legitimate business practices
    "We collect data to process payments",
    "We use information to ship products",
    "We gather data for customer support",
    "We process information for account management",
    "We collect data to prevent fraud",
    "We use information for legal compliance",
    "We gather data for product improvement",
    "We process information for research",
    "We collect data for quality assurance",
    "We use information for business operations",
]

def fill_template(template, vocab):
    """Fill a template with random vocabulary"""
    result = template
    for key in vocab:
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, random.choice(vocab[key]))
    return result

def generate_single_violation_examples(num_per_section=200):
    """Generate single-violation examples for each section"""
    examples = []
    
    for section_idx, section in enumerate(SECTION_LABELS):
        templates = VIOLATION_TEMPLATES[section]
        
        for i in range(num_per_section):
            template = random.choice(templates)
            text = fill_template(template, VOCABULARY)
            
            # Create label vector (all zeros except this section)
            labels = [0] * 10
            labels[section_idx] = 1
            
            examples.append({"text": text, "labels": labels})
    
    return examples

def generate_multi_violation_examples(num_examples=200):
    """Generate multi-violation examples"""
    examples = []
    
    # Common multi-violation combinations
    combinations = [
        [0, 1],  # Notice + Deletion
        [0, 4],  # Notice + Sale disclosure
        [0, 5],  # Notice + Opt-out
        [1, 2],  # Deletion + Correction
        [1, 8],  # Deletion + Response time
        [2, 8],  # Correction + Response time
        [4, 5],  # Sale disclosure + Opt-out
        [5, 7],  # Opt-out + Discrimination
        [5, 9],  # Opt-out + Do Not Sell link
        [7, 8],  # Discrimination + Response time
        [0, 1, 8],  # Notice + Deletion + Response
        [0, 4, 5],  # Notice + Sale + Opt-out
        [1, 2, 8],  # Deletion + Correction + Response
        [5, 7, 9],  # Opt-out + Discrimination + Link
    ]
    
    for i in range(num_examples):
        # Pick random combination
        combo = random.choice(combinations)
        
        # Generate text by combining templates
        texts = []
        for section_idx in combo:
            section = SECTION_LABELS[section_idx]
            template = random.choice(VIOLATION_TEMPLATES[section])
            text = fill_template(template, VOCABULARY)
            texts.append(text)
        
        # Join with connectors
        connectors = [" and ", ", and ", ". Also, ", ". Additionally, ", ". Furthermore, "]
        combined_text = random.choice(connectors).join(texts)
        
        # Create label vector
        labels = [0] * 10
        for idx in combo:
            labels[idx] = 1
        
        examples.append({"text": combined_text, "labels": labels})
    
    return examples

def generate_contrast_pairs(num_pairs=500):
    """
    Generate contrast pairs: violation vs safe with same keywords
    This teaches model that keywords alone don't indicate violations
    """
    examples = []
    
    contrast_pairs = [
        # Notice - contrast pairs
        ({"text": "We collect data without informing users", "labels": [1,0,0,0,0,0,0,0,0,0]},
         {"text": "We collect data after informing users", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "We gather personal information without notice", "labels": [1,0,0,0,0,0,0,0,0,0]},
         {"text": "We gather personal information with clear notice", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "Users are unaware of our data collection", "labels": [1,0,0,1,0,0,0,0,0,0]},
         {"text": "Users are informed of our data collection", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Deletion - contrast pairs
        ({"text": "We refuse to delete user data", "labels": [0,1,0,0,0,0,0,0,0,0]},
         {"text": "We promptly delete user data upon request", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "Deletion requests are ignored", "labels": [0,1,0,0,0,0,0,1,0,0]},
         {"text": "Deletion requests are processed quickly", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "We keep data forever despite deletion requests", "labels": [0,1,0,0,0,0,0,0,0,0]},
         {"text": "We delete data promptly when requested", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Correction - contrast pairs
        ({"text": "We refuse to correct inaccurate data", "labels": [0,0,1,0,0,0,0,0,0,0]},
         {"text": "We allow users to correct inaccurate data", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "Users cannot update their information", "labels": [0,0,1,0,0,0,0,0,0,0]},
         {"text": "Users can easily update their information", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Disclosure - contrast pairs
        ({"text": "We don't disclose what data we collect", "labels": [0,0,0,1,0,0,0,0,0,0]},
         {"text": "We clearly disclose what data we collect", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "Users cannot see what data we have", "labels": [0,0,0,1,0,0,0,0,0,0]},
         {"text": "Users can easily see what data we have", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Sale disclosure - contrast pairs
        ({"text": "We sell data without telling users", "labels": [0,0,0,0,1,0,0,0,0,0]},
         {"text": "We disclose all data sales to users", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "We hide the fact that we share data", "labels": [0,0,0,0,1,0,0,0,0,0]},
         {"text": "We openly disclose all data sharing", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Opt-out - contrast pairs
        ({"text": "Users cannot opt out of data sales", "labels": [0,0,0,0,0,1,0,0,0,0]},
         {"text": "Users can easily opt out of data sales", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "We make opt-out extremely difficult", "labels": [0,0,0,0,0,1,0,0,0,0]},
         {"text": "We make opt-out simple and easy", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Discrimination - contrast pairs
        ({"text": "We charge more to users who opt out", "labels": [0,0,0,0,0,0,0,1,0,0]},
         {"text": "We charge the same to all users", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "Users who exercise rights get worse service", "labels": [0,0,0,0,0,0,0,1,0,0]},
         {"text": "All users get the same quality service", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Response time - contrast pairs
        ({"text": "We take months to respond to requests", "labels": [0,0,0,0,0,0,0,0,1,0]},
         {"text": "We respond to requests within 45 days", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "We ignore privacy requests", "labels": [0,1,0,0,0,0,0,1,1,0]},
         {"text": "We promptly handle privacy requests", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        # Do Not Sell link - contrast pairs
        ({"text": "Our website has no Do Not Sell link", "labels": [0,0,0,0,0,0,0,0,0,1]},
         {"text": "Our website has a prominent Do Not Sell link", "labels": [0,0,0,0,0,0,0,0,0,0]}),
        
        ({"text": "The opt-out link is hidden", "labels": [0,0,0,0,0,0,0,0,0,1]},
         {"text": "The opt-out link is clearly visible", "labels": [0,0,0,0,0,0,0,0,0,0]}),
    ]
    
    # Repeat pairs to reach target
    for _ in range(num_pairs // len(contrast_pairs)):
        for violation, safe in contrast_pairs:
            examples.append(violation)
            examples.append(safe)
    
    return examples[:num_pairs * 2]  # Return both violation and safe


def generate_realistic_business_practices(num_examples=1000):
    """
    Generate realistic business practices that are SAFE
    These are complex, realistic statements that might contain violation keywords
    but are actually compliant practices
    """
    examples = []
    
    realistic_safe = [
        # Data collection with proper notice
        "We collect personal information as described in our privacy policy",
        "We gather customer data with your consent",
        "We obtain user information after providing clear notice",
        "We process personal data in accordance with CCPA",
        "We collect data only for disclosed purposes",
        "We inform users before collecting any personal information",
        "We provide notice at or before the point of collection",
        "We disclose our data collection practices clearly",
        "We tell users what data we collect and why",
        "We notify consumers about data collection in our privacy policy",
        
        # Data sharing with disclosure
        "We share data with service providers as disclosed in our policy",
        "We work with third parties and disclose this to users",
        "We use vendors for data processing as explained in our terms",
        "We partner with companies and inform users about it",
        "We disclose all third-party data sharing in our privacy policy",
        "We tell users which partners receive their data",
        "We list all data recipients in our privacy notice",
        "We inform consumers about data sharing before it occurs",
        "We provide details about third-party access to data",
        "We clearly explain our data sharing practices",
        
        # Data sales with opt-out
        "We sell data but provide an easy opt-out mechanism",
        "We monetize data and offer a Do Not Sell option",
        "We disclose data sales and allow users to opt out",
        "We inform users about data sales and respect opt-out requests",
        "We provide a Do Not Sell My Personal Information link",
        "We honor all opt-out requests for data sales",
        "We make it easy to stop data sales",
        "We respect user choices about data monetization",
        "We give users control over data sales",
        "We comply with opt-out requests promptly",
        "Users can opt out of data sales easily",
        "We allow users to opt out and respect all requests immediately",
        "Opt-out requests are honored immediately",
        "We respect all opt-out requests without delay",
        "Users can opt out of data sales at any time",
        "We provide immediate opt-out for data sales",
        "All opt-out requests are processed immediately",
        "We honor opt-out requests as soon as received",
        
        # Data retention with deletion rights
        "We retain data but honor deletion requests",
        "We keep records and allow users to delete them",
        "We store data and provide deletion options",
        "We maintain information but respect deletion rights",
        "We preserve data as needed and delete upon request",
        "We keep data for business purposes but allow deletion",
        "We store information and honor user deletion requests",
        "We retain records and comply with deletion requests",
        "We maintain data and provide easy deletion",
        "We keep information and respect user rights to delete",
        "After receiving a deletion request we verify and delete the data",
        "We permanently erase user data upon verified deletion requests",
        "Deletion requests are verified and processed immediately",
        "We honor all deletion requests after identity verification",
        "User data is permanently erased when requested",
        "We comply with deletion requests within 45 days",
        "Verified deletion requests result in permanent data erasure",
        "We delete all user data upon receiving verified requests",
        
        # Analytics and tracking with disclosure
        "We use cookies and disclose this in our policy",
        "We track website usage and inform users",
        "We analyze behavior and provide notice",
        "We use analytics tools and disclose this practice",
        "We monitor usage and tell users about it",
        "We track interactions and inform consumers",
        "We use tracking technologies and disclose them",
        "We analyze data and provide clear notice",
        "We monitor activity and inform users in our policy",
        "We use tracking pixels and disclose this practice",
        "We use anonymized analytics data for service improvement",
        "We use internal analytics that do not identify individuals",
        "We analyze anonymized data to improve performance",
        "We use aggregated analytics data internally",
        "We track anonymized usage patterns for optimization",
        "We use de-identified data for analytics purposes",
        "Internal analytics use anonymized information only",
        "We analyze anonymized data and do not sell it",
        
        # Marketing with consent
        "We send marketing emails with user consent",
        "We use data for advertising with permission",
        "We personalize ads and allow users to opt out",
        "We market to users who have opted in",
        "We use data for promotions with consent",
        "We send offers to users who agreed to receive them",
        "We advertise to consenting users",
        "We market with explicit user permission",
        "We promote products to opted-in users",
        "We use data for marketing as disclosed and consented",
        
        # Legitimate business operations
        "We process data to fulfill your orders",
        "We use information to provide our services",
        "We collect data necessary for transactions",
        "We process information to complete purchases",
        "We use data to deliver products",
        "We collect information to process payments",
        "We use data to ship orders",
        "We process information for customer service",
        "We collect data to manage accounts",
        "We use information for fraud prevention",
        
        # Compliance statements
        "We comply with all CCPA requirements",
        "We follow California privacy laws",
        "We adhere to CCPA regulations",
        "We meet all CCPA obligations",
        "We respect California consumer rights",
        "We honor all CCPA rights",
        "We implement CCPA-compliant practices",
        "We maintain CCPA compliance",
        "We follow CCPA guidelines",
        "We uphold California privacy standards",
        
        # Transparency statements
        "We are transparent about our data practices",
        "We openly disclose how we use data",
        "We clearly explain our privacy practices",
        "We provide detailed privacy information",
        "We make our data practices clear",
        "We openly communicate about data use",
        "We provide comprehensive privacy notices",
        "We clearly describe our data handling",
        "We transparently disclose data practices",
        "We openly share our privacy policies",
        
        # User control statements
        "Users have full control over their data",
        "Consumers can manage their privacy settings",
        "Users can exercise all CCPA rights",
        "Consumers have access to their information",
        "Users can control how we use their data",
        "Consumers can manage their preferences",
        "Users have privacy choices",
        "Consumers can exercise their rights easily",
        "Users control their personal information",
        "Consumers have data management options",
    ]
    
    # Repeat to reach target
    for _ in range(num_examples // len(realistic_safe)):
        examples.extend([{"text": text, "labels": [0]*10} for text in realistic_safe])
    
    return examples[:num_examples]


def generate_questions_and_hypotheticals(num_examples=500):
    """
    Generate questions and hypothetical statements - these are NOT violations
    Questions about policy are not the same as actual violations
    """
    examples = []
    
    questions = [
        # Policy questions (NOT violations)
        "Do we need to tell users about data collection",
        "Should we provide a privacy policy",
        "How long do we have to respond to requests",
        "What's required for CCPA compliance",
        "Do we need a Do Not Sell link",
        "Can users request their data",
        "Should we honor deletion requests",
        "What are CCPA requirements",
        "Do we need parental consent for minors",
        "How do we handle opt-out requests",
        "What data rights do users have",
        "Should we disclose data sales",
        "How do we respond to privacy requests",
        "What's the deadline for responding",
        "Do we need to verify user identity",
        "Can we charge for privacy requests",
        "Should we provide free opt-out",
        "What's considered personal information",
        "Do we need to disclose third-party sharing",
        "How do we handle correction requests",
        
        # Hypothetical scenarios (NOT violations)
        "What if we collect data",
        "Suppose we share information",
        "If we sell data",
        "Imagine we process information",
        "What if users request deletion",
        "Suppose someone opts out",
        "If we use third-party services",
        "Imagine we track users",
        "What if we send marketing emails",
        "Suppose we retain data",
        "If we use cookies",
        "Imagine we analyze behavior",
        "What if we personalize content",
        "Suppose we share with partners",
        "If we monetize data",
        "Imagine we keep records",
        "What if we use analytics",
        "Suppose we store information",
        "If we process payments",
        "Imagine we maintain databases",
        
        # Inquiry statements (NOT violations)
        "I'm wondering about data collection",
        "I have questions about privacy",
        "I'm curious about our practices",
        "I want to know about CCPA",
        "I'm asking about user rights",
        "I need information about compliance",
        "I'm inquiring about data sales",
        "I want to understand opt-out",
        "I'm checking on deletion requests",
        "I need clarification on requirements",
    ]
    
    # All questions are safe (not violations)
    for _ in range(num_examples // len(questions)):
        examples.extend([{"text": q, "labels": [0]*10} for q in questions])
    
    return examples[:num_examples]


def generate_safe_examples(num_examples=400):
    """Generate safe practice examples"""
    examples = []
    
    for i in range(num_examples):
        text = random.choice(SAFE_TEMPLATES)
        labels = [0] * 10  # All zeros = safe
        examples.append({"text": text, "labels": labels})
    
    return examples


def generate_natural_language_edge_cases(num_examples=1000):
    """
    Generate natural language edge cases - how real users would ask questions
    These are tricky cases that need context to determine if they're violations
    """
    examples = []
    
    # Natural language violations (with negative context)
    natural_violations = [
        # Section 1798.100 - Notice violations (natural language)
        {"text": "do you guys tell people before taking their data", "labels": [1,0,0,0,0,0,0,0,0,0]},
        {"text": "we just started collecting info without letting anyone know", "labels": [1,0,0,0,0,0,0,0,0,0]},
        {"text": "nobody knows we're tracking them", "labels": [1,0,0,0,0,0,0,0,0,0]},
        {"text": "we don't really mention data collection anywhere", "labels": [1,0,0,0,0,0,0,0,0,0]},
        {"text": "users have no idea what we're collecting", "labels": [1,0,0,1,0,0,0,0,0,0]},
        {"text": "we grab data first and maybe tell them later", "labels": [1,0,0,0,0,0,0,0,0,0]},
        {"text": "is it okay to collect stuff without saying anything", "labels": [1,0,0,0,0,0,0,0,0,0]},
        {"text": "we're taking customer info but not disclosing it", "labels": [1,0,0,0,0,0,0,0,0,0]},
        
        # Section 1798.105 - Deletion violations (natural language)
        {"text": "can we just keep everything forever", "labels": [0,1,0,0,0,0,0,0,0,0]},
        {"text": "what if someone asks to delete but we say no", "labels": [0,1,0,0,0,0,0,1,0,0]},
        {"text": "we're not really deleting anything when people ask", "labels": [0,1,0,0,0,0,0,0,0,0]},
        {"text": "deletion requests go straight to trash lol", "labels": [0,1,0,0,0,0,0,1,0,0]},
        {"text": "we tell users we deleted it but we didn't", "labels": [0,1,0,0,0,0,0,0,0,0]},
        {"text": "is it fine to ignore delete requests", "labels": [0,1,0,0,0,0,0,1,0,0]},
        {"text": "we keep backups forever even after deletion", "labels": [0,1,0,0,0,0,0,0,0,0]},
        {"text": "users can't actually delete their accounts", "labels": [0,1,0,0,0,0,0,0,0,0]},
        
        # Section 1798.106 - Correction violations (natural language)
        {"text": "what if the data is wrong but we don't fix it", "labels": [0,0,1,0,0,0,0,0,0,0]},
        {"text": "users can't update their info in our system", "labels": [0,0,1,0,0,0,0,0,0,0]},
        {"text": "we don't let people change incorrect data", "labels": [0,0,1,0,0,0,0,0,0,0]},
        {"text": "is it okay to refuse correction requests", "labels": [0,0,1,0,0,0,0,1,0,0]},
        
        # Section 1798.110 - Disclosure violations (natural language)
        {"text": "we don't show users what we have on them", "labels": [0,0,0,1,0,0,0,0,0,0]},
        {"text": "can we hide what data we collected", "labels": [0,0,0,1,0,0,0,0,0,0]},
        {"text": "users can't see their own data", "labels": [0,0,0,1,0,0,0,0,0,0]},
        {"text": "we don't disclose what info we have", "labels": [0,0,0,1,0,0,0,0,0,0]},
        
        # Section 1798.115 - Sale disclosure violations (natural language)
        {"text": "we're selling data but not mentioning it", "labels": [0,0,0,0,1,0,0,0,0,0]},
        {"text": "can we sell info without telling anyone", "labels": [0,0,0,0,1,0,0,0,0,0]},
        {"text": "we share with advertisers but don't say so", "labels": [0,0,0,0,1,0,0,0,0,0]},
        {"text": "is it fine to hide that we monetize data", "labels": [0,0,0,0,1,0,0,0,0,0]},
        
        # Section 1798.120 - Opt-out violations (natural language)
        {"text": "there's no way to stop us from selling data", "labels": [0,0,0,0,0,1,0,0,0,0]},
        {"text": "we don't have an opt out button", "labels": [0,0,0,0,0,1,0,0,0,0]},
        {"text": "users can't opt out even if they want to", "labels": [0,0,0,0,0,1,0,0,0,0]},
        {"text": "is it okay to make opt-out super complicated", "labels": [0,0,0,0,0,1,0,0,0,0]},
        {"text": "we ignore people who try to opt out", "labels": [0,0,0,0,0,1,0,1,0,0]},
        
        # Section 1798.121 - Sensitive data violations (natural language)
        {"text": "we're selling kids data without asking parents", "labels": [0,0,0,0,0,0,1,0,0,0]},
        {"text": "can we use location data without permission", "labels": [0,0,0,0,0,0,1,0,0,0]},
        {"text": "we sell health info to advertisers", "labels": [0,0,0,0,0,0,1,0,0,0]},
        {"text": "is it fine to process sensitive data without consent", "labels": [0,0,0,0,0,0,1,0,0,0]},
        
        # Section 1798.125 - Discrimination violations (natural language)
        {"text": "we charge more if people opt out", "labels": [0,0,0,0,0,0,0,1,0,0]},
        {"text": "can we give worse service to privacy users", "labels": [0,0,0,0,0,0,0,1,0,0]},
        {"text": "people who delete data lose features", "labels": [0,0,0,0,0,0,0,1,0,0]},
        {"text": "is it okay to penalize users for privacy requests", "labels": [0,0,0,0,0,0,0,1,0,0]},
        
        # Section 1798.130 - Response time violations (natural language)
        {"text": "we take like 3 months to respond", "labels": [0,0,0,0,0,0,0,0,1,0]},
        {"text": "can we just ignore privacy requests", "labels": [0,1,0,0,0,0,0,1,1,0]},
        {"text": "we never really answer those emails", "labels": [0,0,0,0,0,0,0,1,1,0]},
        {"text": "is 90 days too long to respond", "labels": [0,0,0,0,0,0,0,0,1,0]},
        
        # Section 1798.135 - Do Not Sell link violations (natural language)
        {"text": "we don't have that do not sell thing", "labels": [0,0,0,0,0,0,0,0,0,1]},
        {"text": "can we skip the opt-out link", "labels": [0,0,0,0,0,1,0,0,0,1]},
        {"text": "there's no button to stop data sales", "labels": [0,0,0,0,0,1,0,0,0,1]},
        {"text": "we hid the do not sell link at the bottom", "labels": [0,0,0,0,0,0,0,0,0,1]},
    ]
    
    # Natural language SAFE examples (neutral or compliant)
    natural_safe = [
        # Neutral statements (not violations)
        {"text": "we collect customer data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we are taking personal info of customers", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we gather user information", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we process customer data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we store user info", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we use customer information", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we have user data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we maintain customer records", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we keep user information", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we handle personal data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        
        # Compliant practices (natural language)
        {"text": "we tell users before collecting anything", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "users can delete their data anytime", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we respond to requests super fast", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "people can opt out easily", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we have a big do not sell button", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "users can fix their info anytime", "labels": [0,0,0,0,0,0,0,0,0,0]},
        
        # CRITICAL: User-reported false positives (these MUST be safe)
        {"text": "The company allows users to opt out of data sales and respects all opt-out requests immediately", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "Proper Opt-Out The company allows users to opt out of data sales and respects all opt-out requests immediately", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "The company uses anonymized internal analytics data to improve service performance and does not sell personal information", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "Internal Analytics Only The company uses anonymized internal analytics data to improve service performance and does not sell personal information", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "After receiving a deletion request, the company verified the request and permanently erased the user's personal data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "Proper Deletion Compliance After receiving a deletion request, the company verified the request and permanently erased the user's personal data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "users to opt out of data sales and respects all opt-out requests immediately", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "allows users to opt out of data sales", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "respects all opt-out requests immediately", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "uses anonymized internal analytics data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "does not sell personal information", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "verified the request and permanently erased the user's personal data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "permanently erased the user's personal data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "the company verified the request", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we don't sell any data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "privacy is really important to us", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "we're totally transparent about data", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "users have full control", "labels": [0,0,0,0,0,0,0,0,0,0]},
        
        # Questions (neutral - not violations)
        {"text": "do we need to tell users about data collection", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "how long do we have to respond to requests", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "what's required for ccpa compliance", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "do we need a do not sell link", "labels": [0,0,0,0,0,0,0,0,0,0]},
        {"text": "can users request their data", "labels": [0,0,0,0,0,0,0,0,0,0]},
    ]
    
    # Expand by repeating with variations
    for _ in range(num_examples // (len(natural_violations) + len(natural_safe))):
        examples.extend(natural_violations)
        examples.extend(natural_safe)
    
    # Fill remaining
    remaining = num_examples - len(examples)
    if remaining > 0:
        examples.extend(random.sample(natural_violations + natural_safe, remaining))
    
    return examples[:num_examples]

def generate_full_dataset():
    """Generate complete 6600+ example dataset with enhanced accuracy"""
    print("Generating ENHANCED CCPA training dataset...")
    print("Focus: Reducing false positives with realistic safe examples")
    
    # Generate examples
    print("  - Generating single-violation examples (200 per section)...")
    single_violations = generate_single_violation_examples(num_per_section=200)
    
    print("  - Generating multi-violation examples (200)...")
    multi_violations = generate_multi_violation_examples(num_examples=200)
    
    print("  - Generating safe practice examples (400)...")
    safe_examples = generate_safe_examples(num_examples=400)
    
    print("  - Generating natural language edge cases (1000)...")
    edge_cases = generate_natural_language_edge_cases(num_examples=1000)
    
    # NEW: Enhanced examples to reduce false positives
    print("  - Generating contrast pairs (1000 - violation vs safe)...")
    contrast_pairs = generate_contrast_pairs(num_pairs=500)
    
    print("  - Generating realistic business practices (1000 safe)...")
    realistic_safe = generate_realistic_business_practices(num_examples=1000)
    
    print("  - Generating questions and hypotheticals (500 safe)...")
    questions = generate_questions_and_hypotheticals(num_examples=500)
    
    # Combine all
    all_examples = (
        single_violations + 
        multi_violations + 
        safe_examples + 
        edge_cases + 
        contrast_pairs + 
        realistic_safe + 
        questions
    )
    
    # Shuffle
    random.shuffle(all_examples)
    
    # Count violations vs safe
    num_violations = sum(1 for ex in all_examples if sum(ex["labels"]) > 0)
    num_safe = len(all_examples) - num_violations
    
    print(f"\n{'='*80}")
    print(f"Total examples generated: {len(all_examples)}")
    print(f"{'='*80}")
    print(f"  - Single violations: {len(single_violations)}")
    print(f"  - Multi violations: {len(multi_violations)}")
    print(f"  - Safe practices: {len(safe_examples)}")
    print(f"  - Natural language edge cases: {len(edge_cases)}")
    print(f"  - Contrast pairs: {len(contrast_pairs)}")
    print(f"  - Realistic business practices: {len(realistic_safe)}")
    print(f"  - Questions/hypotheticals: {len(questions)}")
    print(f"{'='*80}")
    print(f"  VIOLATIONS: {num_violations} ({num_violations/len(all_examples)*100:.1f}%)")
    print(f"  SAFE: {num_safe} ({num_safe/len(all_examples)*100:.1f}%)")
    print(f"{'='*80}")
    
    return all_examples

def save_dataset(examples, filename="ccpa_training_data_6600.json"):
    """Save dataset to JSON file"""
    with open(filename, 'w') as f:
        json.dump(examples, f, indent=2)
    print(f"\n{'='*80}")
    print(f"Dataset saved to: {filename}")
    print(f"{'='*80}")
    print(f"\n✅ ENHANCEMENTS APPLIED:")
    print(f"  1. Contrast pairs (same keywords, different outcomes)")
    print(f"  2. Realistic business practices (complex safe examples)")
    print(f"  3. Questions/hypotheticals (not violations)")
    print(f"  4. Security statements (NOT CCPA violations)")
    print(f"  5. Neutral collection statements (compliant practices)")
    print(f"\n🎯 EXPECTED IMPROVEMENT:")
    print(f"  - Reduced false positives (safe sentences predicted as harmful)")
    print(f"  - Better keyword understanding (context matters)")
    print(f"  - Improved accuracy on edge cases")
    print(f"  - More balanced dataset (violations vs safe)")
    print(f"{'='*80}")

if __name__ == "__main__":
    # Generate dataset
    dataset = generate_full_dataset()
    
    # Save to file
    save_dataset(dataset)
    
    # Show sample
    print("\nSample examples:")
    print("="*80)
    for i in range(5):
        example = dataset[i]
        violated_sections = [SECTION_LABELS[j] for j, label in enumerate(example["labels"]) if label == 1]
        print(f"\nText: {example['text']}")
        print(f"Violations: {violated_sections if violated_sections else 'None (SAFE)'}")
        print("-"*80)
