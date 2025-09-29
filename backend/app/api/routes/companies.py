"""
Company Data Management API Routes
"""

from datetime import datetime
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends

from app.services.data_pipeline import DataPipeline

router = APIRouter()


async def get_data_pipeline() -> AsyncGenerator[DataPipeline, None]:
    """
    Dependency injection for DataPipeline service.

    Provides a DataPipeline instance with proper resource cleanup.
    """
    pipeline = DataPipeline()
    try:
        yield pipeline
    finally:
        await pipeline.cleanup()


@router.post("/collect-info/{symbol}")
async def collect_stock_info(
    symbol: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Collect and store basic company information for a specific symbol.

    Retrieves fundamental company data from external APIs (Alpha Vantage)
    including company name, sector, industry, market cap, and key financial
    ratios. This information is stored in the database for future reference
    and analysis.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT') - automatically converted to uppercase

    Returns:
        dict: Collection result containing:
            - message: Success/failure message
            - symbol: Processed symbol (uppercase)
            - success: Boolean indicating operation success

    Raises:
        HTTPException: 500 if data collection fails

    Note:
        Respects Alpha Vantage API rate limits (5 calls/min, 500 calls/day).
        Duplicate requests for same symbol within 24 hours may return cached data.
    """
    try:
        success = await pipeline.collect_stock_info(symbol.upper())

        if success:
            return {
                "message": f"Stock info collected for {symbol}",
                "symbol": symbol.upper(),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to collect info for {symbol}",
                "symbol": symbol.upper(),
                "success": False,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-data/{symbol}")
async def collect_daily_data(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Collect historical daily price data for a specific symbol.

    Retrieves OHLCV (Open, High, Low, Close, Volume) daily price data
    for the specified symbol and date range. If no dates are provided,
    collects maximum available historical data. Data is validated,
    adjusted for splits/dividends, and stored in DuckDB for fast access.

    Args:
        symbol: Stock symbol (e.g., 'AAPL') - automatically converted to uppercase
        start_date: Optional start date for data collection (defaults to earliest available)
        end_date: Optional end date for data collection (defaults to latest available)

    Returns:
        dict: Collection result containing:
            - message: Detailed success/failure message
            - symbol: Processed symbol (uppercase)
            - start_date: Actual start date used
            - end_date: Actual end date used
            - success: Boolean indicating operation success

    Raises:
        HTTPException: 500 if data collection fails

    Note:
        Large date ranges may take several minutes to complete.
        Data is automatically cached to minimize API calls.
    """
    try:
        success = await pipeline.collect_daily_data(
            symbol.upper(), start_date, end_date
        )

        if success:
            return {
                "message": f"Daily data collected for {symbol}",
                "symbol": symbol.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "success": True,
            }
        else:
            return {
                "message": f"Failed to collect data for {symbol}",
                "symbol": symbol.upper(),
                "success": False,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage/{symbol}")
async def get_symbol_coverage(
    symbol: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Get detailed data coverage information for a specific symbol.

    Returns comprehensive information about the availability and quality
    of data for the specified symbol, including date ranges, data gaps,
    last update timestamps, and data quality metrics.

    Args:
        symbol: Stock symbol to check coverage for (automatically converted to uppercase)

    Returns:
        dict: Coverage information containing:
            - symbol: Processed symbol
            - date_range: Start and end dates of available data
            - total_records: Number of data points available
            - gaps: List of date ranges with missing data
            - last_updated: Timestamp of most recent data update
            - data_quality: Quality metrics (completeness, accuracy scores)

    Raises:
        HTTPException: 500 if coverage check fails
        HTTPException: 404 if symbol not found in database
    """
    try:
        coverage = await pipeline._get_symbol_coverage(symbol.upper())
        return coverage

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{symbol}")
async def get_company_info(
    symbol: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Retrieve stored company information for a specific symbol.

    Returns comprehensive company fundamentals and metadata previously
    collected and stored in the database. This includes financial ratios,
    company description, sector classification, and market data.

    Args:
        symbol: Stock symbol (automatically converted to uppercase)

    Returns:
        dict: Company information containing:
            - symbol: Stock symbol
            - name: Company name
            - description: Business description
            - sector: Industry sector classification
            - industry: Specific industry classification
            - country: Country of incorporation
            - currency: Reporting currency
            - market_cap: Market capitalization (if available)
            - pe_ratio: Price-to-earnings ratio (if available)
            - dividend_yield: Annual dividend yield (if available)
            - updated_at: Last information update timestamp

    Raises:
        HTTPException: 404 if company information not found
        HTTPException: 500 if retrieval fails

    Note:
        If company info not found, use POST /collect-info/{symbol} first.
    """
    try:
        company = await pipeline.get_company_info(symbol.upper())

        if company:
            return {
                "symbol": company.symbol,
                "name": company.name,
                "description": company.description,
                "sector": company.sector,
                "industry": company.industry,
                "country": company.country,
                "currency": company.currency,
                "market_cap": company.market_cap,
                "pe_ratio": company.pe_ratio,
                "dividend_yield": company.dividend_yield,
                "updated_at": company.updated_at,
            }
        else:
            raise HTTPException(
                status_code=404, detail=f"Company information not found for {symbol}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies")
async def get_all_companies(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Retrieve information for all companies in the database.

    Returns a comprehensive list of all companies for which information
    has been collected and stored. Useful for portfolio analysis,
    screening, and getting an overview of available data.

    Returns:
        dict: All companies data containing:
            - companies: List of company objects with key information:
                - symbol: Stock symbol
                - name: Company name
                - sector: Industry sector
                - industry: Specific industry
                - market_cap: Market capitalization
                - updated_at: Last update timestamp
            - total_count: Total number of companies in database

    Raises:
        HTTPException: 500 if retrieval fails

    Note:
        Large datasets may take time to load. Consider pagination for production use.
    """
    try:
        companies = await pipeline.get_all_companies()

        return {
            "companies": [
                {
                    "symbol": company.symbol,
                    "name": company.name,
                    "sector": company.sector,
                    "industry": company.industry,
                    "market_cap": company.market_cap,
                    "updated_at": company.updated_at,
                }
                for company in companies
            ],
            "total_count": len(companies),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
