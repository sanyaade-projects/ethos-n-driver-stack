//
// Copyright © 2018-2020 Arm Limited. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include <cstdint>
#include <map>
#include <vector>

namespace ethosn
{

namespace command_stream
{
class CommandStreamBuffer;
}

namespace support_library
{

enum class BufferType
{
    Input,
    Output,
    ConstantDma,
    ConstantControlUnit,
    Intermediate
};

enum class BufferLocation
{
    None,
    Dram,
    Sram,
};

struct CompilerBufferInfo
{
public:
    CompilerBufferInfo(BufferType type,
                       uint32_t offset,
                       uint32_t size,
                       BufferLocation location,
                       const std::vector<uint8_t>& constantData,
                       uint32_t sourceOperationId,
                       uint32_t sourceOperationOutputIndex)
        : m_Type(type)
        , m_Offset(offset)
        , m_Size(size)
        , m_Location(location)
        , m_ConstantData(constantData)
        , m_SourceOperationId(sourceOperationId)
        , m_SourceOperationOutputIndex(sourceOperationOutputIndex)
    {}

    BufferType m_Type;
    uint32_t m_Offset;
    uint32_t m_Size;
    BufferLocation m_Location;
    std::vector<uint8_t> m_ConstantData;      ///< May be empty if this buffer is not constant.
    uint32_t m_SourceOperationId;             ///< Only relevant for input and output buffer infos.
    uint32_t m_SourceOperationOutputIndex;    ///< Only relevant for input and output buffer infos.
};

/// Maintains and builds up the set of buffers required by the compiled network.
class BufferManager
{
public:
    BufferManager();

    /// Adds a new buffer with the given properties. Returns the ID of the buffer.
    /// @{
    uint32_t AddDram(BufferType type, uint32_t size);
    uint32_t AddDramConstant(BufferType type, const std::vector<uint8_t>& constantData);
    uint32_t AddDramInput(uint32_t size, uint32_t sourceOperationId);
    uint32_t AddSram(uint32_t size, uint32_t offset);
    /// @}

    /// Adds the command stream buffer, which always has an ID of zero.
    void AddCommandStream(const ethosn::command_stream::CommandStreamBuffer& cmdStream);

    /// Changes the given buffer into an output.
    void ChangeToOutput(uint32_t bufferId, uint32_t sourceOperationId, uint32_t sourceOperationOutputIndex);

    /// If the given buffer is an SRAM buffer then returns the offset in SRAM of the given buffer,
    /// otherwise returns zero.
    uint32_t GetSramOffset(uint32_t bufferId);

    /// Sets of m_Offset field of all DRAM buffers such that all buffers of each type are laid out contiguously.
    /// Also fills in m_ConstantDmaData and m_ConstantControlUnitData with the concatenated data from all
    /// constant buffers of the corresponding type.
    /// Call this once all buffers have been added.
    void Allocate();

    const std::map<uint32_t, CompilerBufferInfo>& GetBuffers() const;
    const std::vector<uint8_t>& GetConstantDmaData() const;
    const std::vector<uint8_t>& GetConstantControlUnitData() const;

private:
    /// All the buffers we currently know about, looked up by ID.
    /// Note that the order of this map is unimportant but we still use an ordered map so that the
    /// order of iteration is consistent across implementations so that Allocate() will allocate
    /// buffers in the same order.
    std::map<uint32_t, CompilerBufferInfo> m_Buffers;
    uint32_t m_NextDramBufferId;
    uint32_t m_NextSramBufferId;

    std::vector<uint8_t> m_ConstantDmaData;
    std::vector<uint8_t> m_ConstantControlUnitData;
};

}    // namespace support_library
}    // namespace ethosn
