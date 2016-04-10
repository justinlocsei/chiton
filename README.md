# Chiton

This repository contains the source code for the Django application that
provides the API for Cover Your Basics.

## Configuration

In order to run Django commands, you will need to create a JSON configuration
file.  It may be stored anywhere, but it is recommended to place it in the
`config/` directory.  The structure and defaults of the file are as follows,
represented as JavaScript that maps directly to JSON:

```javascript
{
    "admins": [{
        "email": null, // The email address for an admin user
        "name": null   // The full name of an admin user
    }],
    "allowed_hosts": [],                             // The list of allowed hosts
    "amazon_associates_aws_access_key_id": null,     // The access key ID for the Amazon Associates AWS user
    "amazon_associates_tracking_id": null,           // The Amazon Associates tracking ID
    "amazon_associates_aws_secret_access_key": null, // The secret access key for the Amazon Associates AWS user
    "backups_aws_access_key_id": null,               // The access key ID for the AWS backups user
    "backups_aws_secret_access_key": null,           // The secret access key for the AWS backups user
    "backups_s3_bucket": null,                       // The name of the S3 bucket that holds backups
    "database": {
        "engine": null,   // The Django database adapter to use
        "host": null,     // The host for the database
        "name": null,     // The name of the database
        "password": null, // The password for the database user
        "port": null,     // The port for the database
        "user": null      // The database user
    },
    "debug": false,           // Whether to run in debug mode
    "file_logging": false,    // Whether to log to a file
    "log_file": null,         // The absolute path to the log file
    "log_level": "INFO",      // The log level to use
    "secret_key": null,       // The Django secret key to use
    "server_email": null,     // The email address from which server messages are sent
    "shopstyle_uid": null,    // The Shopstyle API UID
    "static_root": null,      // The root directory for static files
    "static_url": "/static/"  // The root URL for static files
}
```

Once you have created this file, set the `CHITON_CONFIG_FILE` environment
variable to the absolute path of the config file.  With this setting in place,
you will now be able to interact with the Django application.

## Management Commands

The following management commands are available:

* `chiton_dumpfixtures`: Create or update fixture files for core data.
* `chiton_ensuresuperuser`: Ensure that a superuser exists with an email,
  username, and password provided as arguments.
* `chiton_loadfixtures`: Load all fixtures for core data.
* `chiton_savesnapshot`: Export a snapshot of all current app data.
