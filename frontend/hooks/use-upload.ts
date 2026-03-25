"use client";

import { useState } from "react";
import axios from "axios";
import { useStrainStore, LabReportData } from "@/lib/store";
import { toast } from "sonner";
import { v4 as uuidv4 } from "uuid";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useUpload() {
  const { addReport, updateReport, setProcessing } = useStrainStore();

  const handleUpload = async (files: File[]) => {
    if (files.length === 0) return;
    
    setProcessing(true);
    
    for (const file of files) {
      const id = uuidv4();
      
      // Add initial pending state
      addReport({
        id,
        file_name: file.name,
        strain_name: "Extracting...",
        cannabinoids: [],
        terpenes: [],
        confidence: 0,
        source_type: file.type,
        status: 'extracting'
      });

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post(`${API_BASE_URL}/extract`, formData, {
          headers: { "Content-Type": "multipart/form-data" }
        });

        const data = response.data;
        updateReport(id, {
          ...data,
          status: 'reviewing'
        });
        
        toast.success(`Extracted: ${file.name}`);
      } catch (error) {
        console.error("Upload failed:", error);
        updateReport(id, { status: 'failed' });
        toast.error(`Failed to extract: ${file.name}`);
      }
    }
    
    setProcessing(false);
  };

  return { handleUpload };
}
