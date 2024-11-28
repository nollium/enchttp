# Encrypted HTTP Server

This project is a simple encrypted HTTP server built using Python. 

It serves files from the local directory with basic XOR obfuscation. 

This is not meant for secure file storage or transmission but can be useful for bypassing basic corporate proxies or adding an obfuscation layer for file transfer.

---

## Features
- Serves files from the current directory.
- Files are XOR-ed with a simple key during download.
- Includes a browser-based decryption mechanism using JavaScript.

---

## Installation

```sh
pip install git+ssh://git@github.com/nollium/enchttp.git
```

---

## Usage

To start the server:

1. Run the server:
   ```
   python encrypted_http_server.py [PORT]
   ```
   - Replace `[PORT]` with the desired port number (default is `8000`).
   - Use `--bind` or `-b` to specify a custom bind address (default is `0.0.0.0`).

   Example:
   ```
   python encrypted_http_server.py 8080
   ```

2. Access the server in your browser:
   ```
   http://<server_address>:<port>
   ```

---

## File Decryption

- Files served by this server are obfuscated using XOR with a fixed key (`42` by default).
- When downloading files through the browser, JavaScript automatically "decrypts" the files for you.

---

## Important Notes

- **Security Warning:** The XOR encryption used in this project is **not secure** and should not be used for sensitive data. This is designed for obfuscation purposes only.
- **Compatibility:** Ensure your browser supports JavaScript for the decryption functionality to work properly.
