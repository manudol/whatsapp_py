import csv
import os
import requests

def list_image_urls():
    IDs = []
    csv_file = "./databases/products_db.csv"
    with open(csv_file, 'r') as file:
        csv_readings = csv.reader(file, delimiter=',')
        for rows in csv_readings:
            record = [rows[0], rows[2]]
            IDs.append(record)
    
    IDs.remove(['product_id', 'image_url'])
    return IDs
        

def execute_download():
    save_dir = 'downloaded_images'
    # Validate that the directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # List of image URLs
    image_urls = list_image_urls()

    file_ids = []

    uploaded_img_urls = []
    
    # List of existing files in the directory
    existing_files = os.listdir(save_dir)

    print(f"Number of existing images: ", len(existing_files), "Number of existing urls: ", len(image_urls))

    print(existing_files)

    if len(existing_files) < len(image_urls):
        

        for f in existing_files:
            file_ids.append(f.removesuffix('.jpg'))

        print("Processing names of file into IDs: ", file_ids)
        
        for img_set in image_urls:
            print(f"Untracked image URLs. Proceeding to upload them...")
            if img_set[0] in file_ids:
                pass
            filename = f"{img_set[0]}.jpg"
            save_path = os.path.join(save_dir, filename)

            try:
                response = requests.get(img_set[1])
                response.raise_for_status()  # Raises an error on a bad status
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                print(f"Image saved to {save_path}")
                uploaded_img_urls.append(f"ID: {img_set[0]}, URL: {img_set[1]}")

            except requests.RequestException as e:
                not_found_image = "./img_not_found.jpg"
                try:
                    with open(not_found_image, 'rb') as nf_img:
                        image_content = nf_img.read()
                    with open(save_path, 'wb') as file:
                        file.write(image_content)
                    print(f"Image not found at {img_set[1]}. Default image saved to {save_path}")
                except IOError as io_error:
                    empty_file_path = os.path.join(save_dir, filename)
                    print(f"Failed to open or write the default image: {io_error}. Created empty image file: {empty_file_path}")

        return print(f"All untracked image URLs uplaoded: ", uploaded_img_urls)


    return print("All images URLs tracked !")


print(execute_download())