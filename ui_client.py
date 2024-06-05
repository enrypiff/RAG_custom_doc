import tkinter as tk
import requests


def send_message():
    query = entry.get("1.0", tk.END).strip()  # Specify the index range for getting the text and remove leading/trailing whitespace

    # Display the message and response in the chatbox
    response = requests.post('http://localhost:5000/chatbot', json={"message": query})
    if response.status_code != 200:
        response_text = f"Error: {response.status_code}"
    else:
        data = response.json()
        message = data["response"]
        sources = data["sources"]
        pages = data["pages"]

    response_text = response.status_code

    chatbox.insert(tk.END, f"You: {query}\n", "user")  # Set the tag "user" for the text
    chatbox.insert(tk.END, f"Bot: {message}\n", "bot")  # Set the tag "bot" for the text
    for source, page in zip(sources, pages):
        chatbox.insert(tk.END, f"Source: {source}, Page: {page + 1}\n", "source") # Set the tag "source" for the text
    chatbox.insert(tk.END, f"\n")
    entry.delete("1.0", tk.END)  # Specify the index range for deleting the text


# Create the main window
window = tk.Tk()
window.title("Chatbot UI")

# Create a text widget to display the chat history
chatbox = tk.Text(window, height=20, width=50)  # Adjust the height and width as desired
# Configure the text widget tags for color and style
chatbox.tag_configure("user", foreground="black", font=("Arial", 12, "bold"))
chatbox.tag_configure("bot", foreground="black", font=("Arial", 12, "italic"))
chatbox.tag_configure("source", foreground="black", font=("Arial", 9, "italic"))
chatbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Automatically resize with the window and add margin

# Create a text widget for user input
entry = tk.Text(window, height=5, width=50)  # Adjust the height and width as desired
entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Automatically resize with the window and add margin

# Create a button to send the message
send_button = tk.Button(window, height=2, width=30, text="Send", command=send_message)
send_button.pack(pady=10)

# Configure the window to be resizable
window.resizable(True, True)

# Start the main event loop
window.mainloop()