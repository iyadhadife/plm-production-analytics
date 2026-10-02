import io


def test_list_files_contains_sources(client):
    names = {f["name"] for f in client.get("/api/files").get_json()}
    assert {"MES_Extraction.xlsx", "PLM_DataSet.xlsx", "ERP_Equipes_Airplus.xlsx"} <= names


def test_excel_table_preview(client):
    response = client.get("/api/files/PLM_DataSet.xlsx/table")
    assert response.status_code == 200
    assert "excel-table" in response.get_data(as_text=True)


def test_upload_rejects_disallowed_extension(client):
    data = {"file": (io.BytesIO(b"x"), "script.exe")}
    assert client.post("/api/upload", data=data, content_type="multipart/form-data").status_code == 400
