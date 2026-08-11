# Roadmap

This document outlines the current and future direction for the Inference Control Plane project.
Our goal is to provide the most reliable, performant, and feature-rich AI inference gateway available.

## Q1 2025: Advanced Routing & Resilience

- [ ] **Custom Model Load Balancing**: Implement Round Robin and Least Connections routing algorithms.
- [ ] **Semantic Caching Enhancements**: Native integration with Qdrant for robust vector-based caching.
- [ ] **Native Google Provider**: First-class support for Google Gemini & Vertex AI models without external proxy dependencies.

## Q2 2025: Enterprise Observability & Control

- [ ] **Custom Budgeting Alerts**: Real-time webhook notifications when tenants hit specific budget thresholds.
- [ ] **Advanced PII Redaction**: Integration with common PII scanning libraries to scrub data before it leaves the VPC.
- [ ] **Multi-region Synchronization**: Robust state sharing (limits, configs) across globally distributed instances.

## Q3 2025: Expanding Ecosystem

- [ ] **Multi-modal Support**: Comprehensive caching and routing for vision and audio models.
- [ ] **Plugin Architecture**: Introduce a Python-based middleware system for custom request interception and modification.

_Note: This roadmap is subject to change based on community feedback and emerging AI trends._
