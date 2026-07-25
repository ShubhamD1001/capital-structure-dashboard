# Problem Statement: Capital Structure and Financial Performance Analysis

## Context

A company's capital structure is the balance between debt and equity it uses to fund itself. That balance shapes how risky the company is, how much it pays to finance its operations, and how much value it returns to shareholders. Investors, analysts, and treasury teams regularly need to assess these structures, but doing so across a large group of companies is slow when the underlying data sits in wide, unwieldy spreadsheets.

## The Problem

Financial data for public companies is easy to obtain but hard to compare at scale. A single dataset can carry forty or more fields per company covering debt, revenue, market value, profitability, and dozens of ratios. Buried in that width are the questions that actually matter. Which companies carry more debt than their earnings can comfortably support? Which industries are the most profitable? Is there a relationship between how much a company borrows and how efficiently it uses its capital?

Answering these questions by reading rows in a spreadsheet is impractical. The numbers are present, but the picture is not.

## Objective

This project builds a Power BI dashboard that turns a flat financial dataset of 226 large companies into a single analytical view of capital structure and financial performance. A user can see how leverage relates to profitability, which sectors generate the strongest margins, and where each company sits relative to its peers.

## Scope

The analysis covers 226 companies across multiple industries using a FY2022 financial snapshot. It focuses on five areas:

- Leverage: how much debt companies carry relative to their earnings
- Profitability: operating margins across companies and industries
- Capital efficiency: how much profit each dollar of capital generates
- Capital structure: the split between debt and equity funding
- Peer comparison: how individual companies and sectors rank against one another

## Approach

The raw data was cleaned in Python to handle missing values and standardise units, then modelled into a star schema in Power BI for efficient querying. Five DAX measures calculate the core metrics: leverage ratio, market debt-to-equity, weighted EBITDA margin, capital efficiency, and total debt. The results are presented through a set of linked visuals that update together as the user filters by industry.

## Outcome

The finished dashboard gives analysts and finance teams a fast way to assess the financial health of a large group of companies without working through raw data by hand. It shows the relationship between debt and profitability, highlights the best and worst structured companies, and provides a reusable template that can be pointed at any similar dataset.
