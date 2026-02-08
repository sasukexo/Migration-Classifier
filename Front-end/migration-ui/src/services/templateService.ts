export const generateTemplate = async (
    file: File,
    accountId: string,
    region: string
) => {

    const formData = new FormData();
    formData.append("file", file);
    formData.append("account_id", accountId);
    formData.append("region", region);

    const response = await fetch(
        `${import.meta.env.VITE_API_URL}/template/generate-mgn-template`,
        {
            method: "POST",
            body: formData,
        }
    );

    if (!response.ok) {
        throw new Error("Template generation failed");
    }

    return response.blob();
};
