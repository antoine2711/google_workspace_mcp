"""
Unit tests for Google Sheets read_sheet_dimensions tool.

Tests column width reading, row height reading, and hidden status.
"""

import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.utils import UserInputError
from gsheets.sheets_tools import _read_sheet_dimensions_impl, read_sheet_dimensions


def create_mock_service():
    """Create a properly configured mock Google Sheets service."""
    mock_service = Mock()

    mock_metadata = {
        "sheets": [
            {
                "properties": {
                    "sheetId": 0,
                    "title": "Sheet1",
                    "gridProperties": {"rowCount": 1000, "columnCount": 26},
                }
            },
            {
                "properties": {
                    "sheetId": 12345,
                    "title": "Courriels (A@B.QC)",
                    "gridProperties": {"rowCount": 500, "columnCount": 6},
                }
            },
        ]
    }

    mock_grid_data = {
        "sheets": [
            {
                "properties": {
                    "sheetId": 12345,
                    "title": "Courriels (A@B.QC)",
                    "gridProperties": {"rowCount": 500, "columnCount": 6},
                },
                "data": [
                    {
                        "columnMetadata": [
                            {"pixelSize": 140},
                            {"pixelSize": 100},
                            {"pixelSize": 260},
                            {"pixelSize": 240},
                            {"pixelSize": 380},
                            {"pixelSize": 90, "hiddenByUser": True},
                        ],
                        "rowMetadata": [
                            {"pixelSize": 30},
                            {"pixelSize": 21},
                        ],
                    }
                ],
            }
        ]
    }

    # spreadsheets().get() can return metadata or grid_data based on ranges
    def get_side_effect(spreadsheetId, fields=None, ranges=None, includeGridData=False):
        mock_req = Mock()
        if ranges or includeGridData:
            mock_req.execute = Mock(return_value=mock_grid_data)
        else:
            mock_req.execute = Mock(return_value=mock_metadata)
        return mock_req

    mock_service.spreadsheets().get.side_effect = get_side_effect
    return mock_service


@pytest.mark.asyncio
async def test_read_sheet_dimensions_impl():
    """Test reading column widths and row heights."""
    mock_service = create_mock_service()

    result = await _read_sheet_dimensions_impl(
        service=mock_service,
        spreadsheet_id="test_sheet_123",
        sheet_name="Courriels (A@B.QC)",
        include_rows=True,
    )

    assert result["spreadsheet_id"] == "test_sheet_123"
    assert result["sheet_name"] == "Courriels (A@B.QC)"
    assert result["sheet_id"] == 12345
    assert result["row_count"] == 500
    assert result["column_count"] == 6

    # Verify column widths
    cols = result["column_sizes"]
    assert cols["A"] == 140
    assert cols["B"] == 100
    assert cols["C"] == 260
    assert cols["D"] == 240
    assert cols["E"] == 380
    assert cols["F"] == 90
    assert result["hidden_columns"] == ["F"]

    # Verify row heights
    rows = result["row_sizes"]
    assert rows[1] == 30
    assert rows[2] == 21


def _unwrap(tool):
    """Peel FastMCP/auth wrappers so unit tests can pass a mock service."""
    fn = tool.fn if hasattr(tool, "fn") else tool
    while hasattr(fn, "__wrapped__"):
        fn = fn.__wrapped__
    return fn


@pytest.mark.asyncio
async def test_read_sheet_dimensions_formatted():
    """Test formatted output of read_sheet_dimensions."""
    mock_service = create_mock_service()

    output = await _unwrap(read_sheet_dimensions)(
        service=mock_service,
        user_google_email="user@example.com",
        spreadsheet_id="test_sheet_123",
        sheet_name="Courriels (A@B.QC)",
        include_rows=False,
    )

    assert 'Sheet: "Courriels (A@B.QC)"' in output
    assert "Grid size: 500 rows x 6 columns" in output
    assert "Column A: 140px" in output
    assert "Column F: 90px (hidden)" in output
    assert '"A": 140' in output


@pytest.mark.asyncio
async def test_read_sheet_dimensions_not_found():
    """Test error when sheet does not exist."""
    mock_service = create_mock_service()

    with pytest.raises(UserInputError) as exc_info:
        await _read_sheet_dimensions_impl(
            service=mock_service,
            spreadsheet_id="test_sheet_123",
            sheet_name="NonexistentSheet",
        )

    assert "not found" in str(exc_info.value)
