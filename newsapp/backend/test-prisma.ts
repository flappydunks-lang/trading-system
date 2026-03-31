import { PrismaClient } from "@prisma/client";
const p = new PrismaClient({ log: [] });
console.log("Constructor works");
p.$disconnect();
