        # if command.startswith("message "):
        #     rest = command.removeprefix("message ").strip().lower()

        #     for contact in CONTACTS:
        #         if rest.startswith(contact):
        #             name = contact
        #             message = rest[len(contact):].strip()

        #             if message:
        #                 funcs.append(asyncio.to_thread(send_whatsapp_message, name, message))
        #             else:
        #                 print("❌ No message provided.")
        #             break
        #     else:
        #         print(f"❌ No contact match found in: '{rest}'")