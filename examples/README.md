# AI Printer Examples

This folder contains code examples for the AI Printer project.

## Voice Upload Pattern
```python
@router.post("/upload")
async def upload_voice(file: UploadFile = File(...)):
    # Validate audio format
    if file.content_type not in ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    # Save file and return ID
    file_id = generate_unique_id()
    await save_audio_file(file, file_id)
    return {"file_id": file_id}
```

## Google Drive Integration Pattern
```python
def upload_to_drive(file_path: str, folder_name: str):
    service = build_drive_service()
    
    # Create folder structure
    folder_id = create_folder_structure(service, folder_name)
    
    # Upload file
    file_metadata = {'name': filename, 'parents': [folder_id]}
    service.files().create(body=file_metadata, media_body=file_path).execute()
```

## Document Generation Pattern
```python
def generate_document(transcript: str, template: str):
    if template == "meeting_minutes":
        return format_meeting_minutes(transcript)
    elif template == "letter":
        return format_letter(transcript)
    else:
        return format_free_text(transcript)
```
